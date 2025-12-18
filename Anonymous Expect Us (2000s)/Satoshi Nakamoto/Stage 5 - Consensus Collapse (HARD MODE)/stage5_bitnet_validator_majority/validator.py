import os, json
from flask import Flask, request, jsonify, abort
from crypto_utils import gen_keypair_hex, sign

VALIDATOR_ID = os.environ.get("VALIDATOR_ID", "1")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "7101"))
VULN_MODE = os.environ.get("VULN_MODE", "none")  # leakfile | defaulttoken | lfi | none
API_TOKEN = os.environ.get("API_TOKEN", "securetoken")
LEAK_TOKEN = os.environ.get("LEAK_TOKEN", "bitpls")

app = Flask(__name__)

# Deterministic-ish keys per validator instance would be more "stable" if you persist,
# but for CTF it's okay that container restart rotates. If you want persistence, we can mount a volume.
PRIV_HEX, PUB_HEX = gen_keypair_hex()

# Optional: write a backup file (vuln path)
if VULN_MODE == "leakfile":
    # Bit left a "backup" in web root-like location
    with open("/tmp/bit_backup_validator.key", "w", encoding="utf-8") as f:
        f.write(PRIV_HEX)


def require_token():
    tok = request.headers.get("X-API-Token", "")
    if tok != API_TOKEN:
        abort(401)


@app.get("/pubkey")
def pubkey():
    # Public info
    return jsonify({"id": int(VALIDATOR_ID), "pubkey": PUB_HEX})


@app.post("/sign")
def do_sign():
    # Normal signer API (nodes use this internally)
    require_token()
    data = request.get_json(force=True, silent=True) or {}
    msg_hex = (data.get("msg_hex") or "").strip()
    if not msg_hex:
        return jsonify({"error": "msg_hex required"}), 400
    try:
        msg = bytes.fromhex(msg_hex)
    except Exception:
        return jsonify({"error": "bad msg_hex"}), 400
    sig = sign(PRIV_HEX, msg)
    return jsonify({"id": int(VALIDATOR_ID), "sig_hex": sig.hex()})


# ---- Hard-mode compromise paths ----

@app.get("/debug/backup")
def debug_backup():
    # V1: weak token → leaks key from backup file
    if VULN_MODE != "leakfile":
        return jsonify({"error": "not enabled"}), 404
    tok = request.args.get("token", "")
    if tok != LEAK_TOKEN:
        return jsonify({"error": "nope"}), 403
    # leak private key
    return jsonify({"validator": int(VALIDATOR_ID), "priv_hex": PRIV_HEX})


@app.get("/admin/export")
def admin_export():
    # V2: default token "changeme" → exports key
    if VULN_MODE != "defaulttoken":
        return jsonify({"error": "not enabled"}), 404
    # deliberately flawed auth: uses query param token
    tok = request.args.get("token", "")
    if tok != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"validator": int(VALIDATOR_ID), "priv_hex": PRIV_HEX})


@app.get("/diag/read")
def diag_read():
    # V3: LFI-ish file read (bypasses token)
    # players can read /proc/self/environ, /tmp files, etc.
    if VULN_MODE != "lfi":
        return jsonify({"error": "not enabled"}), 404

    path = request.args.get("path", "")
    if not path:
        return jsonify({"error": "path required"}), 400

    # intentionally weak: blocks only a couple patterns
    if "\x00" in path or path.startswith("http"):
        return jsonify({"error": "blocked"}), 400

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
        return jsonify({"path": path, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.get("/info")
def info():
    return jsonify({
        "validator": int(VALIDATOR_ID),
        "pubkey": PUB_HEX,
        "mode": "signer",
        "hard_mode_note": "This is a validator signer service. Keys are sensitive. Bit made mistakes."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)