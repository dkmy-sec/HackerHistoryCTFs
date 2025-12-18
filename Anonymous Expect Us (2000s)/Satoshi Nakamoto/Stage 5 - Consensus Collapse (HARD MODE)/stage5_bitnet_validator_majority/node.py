import os, threading, hashlib, json
from flask import Flask, request, jsonify
import requests
from crypto_utils import sha256, u32be, verify, h2b, b2h

NODE_ID = os.environ.get("NODE_ID", "A")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "9001"))
PEERS = [p.strip() for p in os.environ.get("PEERS", "").split(",") if p.strip()]
VALIDATORS = [v.strip() for v in os.environ.get("VALIDATORS", "").split(",") if v.strip()]
GENESIS_SEED = os.environ.get("GENESIS_SEED", "BITHAVEN_BITNET_GENESIS")
REQUIRED_SIGS = int(os.environ.get("REQUIRED_SIGS", "3"))

app = Flask(__name__)

# validator registry: id -> pubkey_hex
VAL_PUBS: dict[int, str] = {}

# block store: hash -> block dict
blocks: dict[str, dict] = {}
best_tip: str | None = None


def fetch_validator_pubs():
    pubs = {}
    for url in VALIDATORS:
        try:
            r = requests.get(f"{url}/pubkey", timeout=1.0)
            j = r.json()
            pubs[int(j["id"])] = j["pubkey"]
        except Exception:
            pass
    return pubs


def header_hash(prev32: bytes, height: int, nonce: int, tx_bytes: bytes, txc: int) -> bytes:
    # What validators sign and nodes verify
    return sha256(prev32 + u32be(height) + nonce.to_bytes(4, "big") + bytes([txc]) + tx_bytes)


def parse_block(raw: bytes) -> dict:
    # Wire:
    # prev(32) | height(u32be) | nonce(u32be) | txc(u8) | [txlen(u16be)|tx]* | sigc(u8) | [id(u8)|siglen(u16be)|sig]*
    if len(raw) < 32 + 4 + 4 + 1 + 1:
        raise ValueError("too short")

    i = 0
    prev = raw[i:i + 32];
    i += 32
    height = int.from_bytes(raw[i:i + 4], "big");
    i += 4
    nonce = int.from_bytes(raw[i:i + 4], "big");
    i += 4
    txc = raw[i];
    i += 1

    txs = []
    tx_bytes_concat = b""
    for _ in range(txc):
        if i + 2 > len(raw): raise ValueError("tx len missing")
        tl = int.from_bytes(raw[i:i + 2], "big");
        i += 2
        if i + tl > len(raw): raise ValueError("tx bytes missing")
        t = raw[i:i + tl];
        i += tl
        tx_bytes_concat += (tl.to_bytes(2, "big") + t)
        txs.append(t.decode("utf-8", errors="replace"))

    if i + 1 > len(raw): raise ValueError("sigc missing")
    sigc = raw[i];
    i += 1

    sigs = []
    for _ in range(sigc):
        if i + 1 + 2 > len(raw): raise ValueError("sig entry missing")
        vid = raw[i];
        i += 1
        sl = int.from_bytes(raw[i:i + 2], "big");
        i += 2
        if i + sl > len(raw): raise ValueError("sig bytes missing")
        sig = raw[i:i + sl];
        i += sl
        sigs.append({"id": int(vid), "sig_hex": sig.hex()})

    hh = header_hash(prev, height, nonce, tx_bytes_concat, txc)
    blk_hash = sha256(hh + raw[32 + 4 + 4 + 1:])  # include tx+sig bytes for uniqueness

    return {
        "hash": b2h(blk_hash),
        "prev": b2h(prev),
        "height": height,
        "nonce": nonce,
        "txs": txs,
        "header_hash": b2h(hh),
        "sigs": sigs,
        "raw_hex": raw.hex(),
    }


def make_genesis() -> dict:
    prev = b"\x00" * 32
    height = 0
    nonce = 0
    tx = f"GENESIS::{GENESIS_SEED}::BITNET".encode()
    txc = 1
    tx_bytes = (len(tx).to_bytes(2, "big") + tx)
    hh = header_hash(prev, height, nonce, tx_bytes, txc)
    # Genesis is self-signed by validators? For realism, we accept unsigned genesis.
    raw = (
            prev + u32be(height) + nonce.to_bytes(4, "big") + bytes([txc]) +
            tx_bytes +
            bytes([0])  # sigc
    )
    g = parse_block(raw)
    g["prev"] = "00" * 32
    return g


def verify_sigs(block: dict) -> tuple[bool, int]:
    # majority: require >= REQUIRED_SIGS distinct valid validator sigs over header_hash
    msg = h2b(block["header_hash"])
    valid_ids = set()
    for s in block["sigs"]:
        vid = s["id"]
        pub = VAL_PUBS.get(vid)
        if not pub:
            continue
        try:
            sig = bytes.fromhex(s["sig_hex"])
        except Exception:
            continue
        if verify(pub, msg, sig):
            valid_ids.add(vid)
    return (len(valid_ids) >= REQUIRED_SIGS, len(valid_ids))


def accept_block(block: dict) -> str:
    global best_tip
    h = block["hash"]
    if h in blocks:
        return "known"

    # genesis
    if block["height"] == 0:
        g = make_genesis()
        if h != g["hash"]:
            return "reject: genesis mismatch"
        blocks[h] = block
        best_tip = h
        return "ok"

    parent = blocks.get(block["prev"])
    if not parent:
        return "reject: unknown parent"
    if block["height"] != parent["height"] + 1:
        return "reject: bad height"

    ok, nvalid = verify_sigs(block)
    if not ok:
        return f"reject: need {REQUIRED_SIGS} sigs; got {nvalid}"

    blocks[h] = block

    # fork choice: highest height; tie: lexicographically smallest hash (deterministic)
    if best_tip is None:
        best_tip = h
    else:
        bh = blocks[best_tip]["height"]
        if block["height"] > bh or (block["height"] == bh and h < best_tip):
            best_tip = h
    return "ok"


def gossip(raw_hex: str):
    for p in PEERS:
        try:
            requests.post(f"{p}/submit", json={"hex": raw_hex}, timeout=0.6)
        except Exception:
            pass


@app.get("/info")
def info():
    return jsonify({
        "node": NODE_ID,
        "peers": PEERS,
        "required_sigs": REQUIRED_SIGS,
        "validators_public": [{"id": vid, "pubkey": pk} for vid, pk in sorted(VAL_PUBS.items())],
        "best_tip": best_tip,
        "best_height": blocks[best_tip]["height"] if best_tip else None,
        "wire_format": "prev(32)|height(u32be)|nonce(u32be)|txc(u8)|[txlen(u16be)|tx]*|sigc(u8)|[id(u8)|siglen(u16be)|sig]*",
        "submit": "POST /submit {hex:<block_hex>}",
        "get_block": "GET /block/<hash>",
        "best": "GET /best",
        "hard_mode_notes": [
            "You MUST produce blocks with >=3 valid validator signatures.",
            "You will likely need to compromise validator signer services to obtain private keys.",
            "No ABI/source required; craft raw block hex."
        ],
        "solve_marker_tx": "CLAIM_FLAG_FOR_BITHAVEN"
    })


@app.get("/best")
def best():
    if not best_tip:
        return jsonify({"error": "no chain"}), 500
    return jsonify({"best_tip": best_tip, "height": blocks[best_tip]["height"]})


@app.get("/block/<h>")
def get_block(h: str):
    b = blocks.get(h)
    if not b:
        return jsonify({"error": "not found"}), 404
    return jsonify({k: b[k] for k in ("hash", "prev", "height", "nonce", "txs", "header_hash", "sigs")})


@app.post("/submit")
def submit():
    data = request.get_json(force=True, silent=True) or {}
    hx = (data.get("hex") or "").strip().lower()
    if not hx or any(c not in "0123456789abcdef" for c in hx):
        return jsonify({"error": "bad hex"}), 400
    try:
        raw = bytes.fromhex(hx)
        blk = parse_block(raw)
    except Exception as e:
        return jsonify({"error": f"parse failed: {e}"}), 400

    res = accept_block(blk)
    if res == "ok":
        threading.Thread(target=gossip, args=(blk["raw_hex"],), daemon=True).start()
    return jsonify({"result": res, "hash": blk["hash"], "best_tip": best_tip})


def boot():
    global VAL_PUBS, best_tip
    VAL_PUBS = fetch_validator_pubs()
    g = make_genesis()
    blocks[g["hash"]] = g
    best_tip = g["hash"]


boot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)