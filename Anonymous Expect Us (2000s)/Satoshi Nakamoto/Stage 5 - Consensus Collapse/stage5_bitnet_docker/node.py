import os, time, json, hashlib, threading
from flask import Flask, request, jsonify
import requests

NODE_ID = os.environ.get("NODE_ID", "A")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "9001"))
PEERS = [p.strip() for p in os.environ.get("PEERS", "").split(",") if p.strip()]
GENESIS_SEED = os.environ.get("GENESIS_SEED", "BITHAVEN_BITNET_GENESIS")

app = Flask(__name__)

# --- Chain storage ---
# blocks_by_hash: hash -> block dict
blocks_by_hash = {}
# tip candidates: hash -> total_work
tips = {}
# best tip
best_tip = None


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def b2h(b: bytes) -> str:
    return b.hex()


def h2b(h: str) -> bytes:
    return bytes.fromhex(h)


def u32be(x: int) -> bytes:
    return x.to_bytes(4, "big", signed=False)


def u64be(x: int) -> bytes:
    return x.to_bytes(8, "big", signed=False)


def parse_block(raw: bytes) -> dict:
    if len(raw) < 32 + 4 + 8 + 4 + 1:
        raise ValueError("too short")

    i = 0
    prev = raw[i:i + 32];
    i += 32
    height = int.from_bytes(raw[i:i + 4], "big");
    i += 4
    work = int.from_bytes(raw[i:i + 8], "big");
    i += 8
    nonce = int.from_bytes(raw[i:i + 4], "big");
    i += 4
    txc = raw[i];
    i += 1

    txs = []
    for _ in range(txc):
        if i + 2 > len(raw):
            raise ValueError("tx len missing")
        tl = int.from_bytes(raw[i:i + 2], "big");
        i += 2
        if i + tl > len(raw):
            raise ValueError("tx bytes missing")
        tx = raw[i:i + tl].decode("utf-8", errors="replace");
        i += tl
        txs.append(tx)

    header = prev + u32be(height) + u64be(work) + u32be(nonce) + bytes([txc])
    blk_hash = sha256(header + raw[32 + 4 + 8 + 4 + 1:])  # include tx bytes for uniqueness

    return {
        "hash": b2h(blk_hash),
        "prev": b2h(prev),
        "height": height,
        "work": work,
        "nonce": nonce,
        "txs": txs,
        "raw_hex": raw.hex()
    }

# "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks - Genesis Block Message - Satoshi Nakamoto.
def make_genesis():
    # Deterministic genesis for all nodes
    prev = b"\x00" * 32
    height = 0
    work = 1
    nonce = 0

    tx = f"GENESIS::{GENESIS_SEED}::BIT::{NODE_ID}".encode()
    txs = [tx.decode()]
    raw = (
            prev +
            u32be(height) +
            u64be(work) +
            u32be(nonce) +
            bytes([1]) +
            (len(tx).to_bytes(2, "big") + tx)
    )
    g = parse_block(raw)
    # force genesis prev to "00.."
    g["prev"] = "00" * 32
    return g


def chain_total_work(tip_hash: str) -> int:
    # compute by walking back (cached via tips dict for known tips)
    if tip_hash in tips:
        return tips[tip_hash]
    blk = blocks_by_hash.get(tip_hash)
    if not blk:
        return 0
    if blk["height"] == 0:
        tips[tip_hash] = blk["work"]
        return blk["work"]
    parent = blocks_by_hash.get(blk["prev"])
    if not parent:
        return 0
    tw = chain_total_work(blk["prev"]) + blk["work"]
    tips[tip_hash] = tw
    return tw


def update_best(tip_hash: str):
    global best_tip
    tw = chain_total_work(tip_hash)
    if best_tip is None:
        best_tip = tip_hash
        return

    best_tw = chain_total_work(best_tip)
    best_h = blocks_by_hash[best_tip]["height"]
    h = blocks_by_hash[tip_hash]["height"]

    # Fork-choice: highest total_work; tie -> highest height
    if (tw > best_tw) or (tw == best_tw and h > best_h):
        best_tip = tip_hash


def accept_block(block: dict) -> str:
    # Minimal checks:
    # - parent exists (except genesis)
    # - height increments
    # HARD MODE VULN: does NOT validate 'work' or any PoW
    h = block["hash"]
    if h in blocks_by_hash:
        return "known"

    if block["height"] == 0:
        # accept genesis if matches our genesis hash
        g = make_genesis()
        if h != g["hash"]:
            return "reject: genesis mismatch"
        blocks_by_hash[h] = block
        update_best(h)
        return "ok"

    parent = blocks_by_hash.get(block["prev"])
    if not parent:
        return "reject: unknown parent"
    if block["height"] != parent["height"] + 1:
        return "reject: bad height"

    blocks_by_hash[h] = block
    update_best(h)
    return "ok"


def gossip_block(raw_hex: str):
    for p in PEERS:
        try:
            requests.post(f"{p}/submit", json={"hex": raw_hex}, timeout=0.6)
        except Exception:
            pass


@app.get("/info")
def info():
    g = make_genesis()
    return jsonify({
        "node": NODE_ID,
        "peers": PEERS,
        "best_tip": best_tip,
        "best_height": blocks_by_hash[best_tip]["height"] if best_tip else None,
        "best_total_work": chain_total_work(best_tip) if best_tip else None,
        "genesis_hash": g["hash"],
        "protocol": {
            "submit": "POST /submit {hex: <block_hex>}",
            "get_block": "GET /block/<hash>",
            "best": "GET /best",
            "note": "Hard mode: you must craft raw block hex. Work is used in fork-choice."
        },
        "wire_format": "prev(32)|height(u32be)|work(u64be)|nonce(u32be)|txc(u8)|[txlen(u16be)|tx...]",
        "hint_selectors": {
            # these are just reminders; not ABI, not chain
            "solve_marker_tx": "CLAIM_FLAG_FOR_BITHAVEN"
        }
    })


@app.get("/best")
def best():
    if not best_tip:
        return jsonify({"error": "no chain"}), 500
    return jsonify(
        {"best_tip": best_tip, "height": blocks_by_hash[best_tip]["height"], "total_work": chain_total_work(best_tip)})


@app.get("/block/<h>")
def get_block(h: str):
    b = blocks_by_hash.get(h)
    if not b:
        return jsonify({"error": "not found"}), 404
    return jsonify({k: b[k] for k in ("hash", "prev", "height", "work", "nonce", "txs")})


@app.post("/submit")
def submit():
    data = request.get_json(force=True, silent=True) or {}
    hx = (data.get("hex") or "").strip().lower()
    if not hx or any(c not in "0123456789abcdef" for c in hx):
        return jsonify({"error": "bad hex"}), 400

    raw = bytes.fromhex(hx)
    try:
        blk = parse_block(raw)
    except Exception as e:
        return jsonify({"error": f"parse failed: {e}"}), 400

    res = accept_block(blk)
    if res == "ok":
        # gossip on accept
        threading.Thread(target=gossip_block, args=(blk["raw_hex"],), daemon=True).start()
    return jsonify({"result": res, "hash": blk["hash"], "best_tip": best_tip})


def boot():
    g = make_genesis()
    blocks_by_hash[g["hash"]] = g
    global best_tip
    best_tip = g["hash"]


boot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)