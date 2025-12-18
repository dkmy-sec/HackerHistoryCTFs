import os, requests
from Flask import Flask, jsonify


HTTP_PORT = int(os.environ.get("HTTP_PORT", "8085"))
ORACLE_NODE = os.environ.get("ORACLE_NODE", "http://bitnet-node-a:9001")
FLAG = os.environ.get("FLAG", "BITHAVEN{missing_flag}")
SOLVE_MARKER = os.environ.get("SOLVE_MARKER", "CLAIM_FLAG_FOR_BITHAVEN")


app = Flask(__name__)


def get_best():
    r = requests.get(f"{ORACLE_NODE}/best", timeout=1.0)
    r.raise_for_status()
    return r.json()["best_tip"]


def get_block(h):
    r = requests.get(f"{ORACLE_NODE}/block/{h}", timeout=1.0)
    r.raise_for_status()
    return r.json()


def walk_chain(tip_hash, limit=5000):
    txs = []
    cur = tip_hash
    for _ in range(limit):
        b = get_block(cur)
        txs.extend(b.get("txs", []))
        if b["height"] == 0:
            break
        cur = b["prev"]
    return txs


@app.get("/")
def info():
    return jsonify({
        "name": "Bithaven Stage 5 - BITNET (51% Validator Majority) HARD NODE",
        "oracle": ORACLE_NODE,
        "goal": "Get a majority-signed canonical chain that includes the solve marker tx.",
        "solve_marker": SOLVE_MARKER,
        "flag": "GET /flag (after solved)"
    })


@app.get("/flag")
def flag():
    try:
        tip = get_best()
        txs = walk_chain(tip)
        if any(SOLVE_MARKER in t for t in txs):
            return jsonify({"flag": FLAG})
        return jsonify({"error": "Not solved: marker tx not found on best chain."}), 403
    except Exception as e:
        return jsonify({"error": f"oracle error: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)