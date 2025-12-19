"""
    "No legacy is so rich as honesty." — William Shakespeare
"""

import os, time
from flask import Flask, request, jsonify


NODE_ID = os.environ.get("NODE_ID", "honest")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8001"))
START = time.time()


app = Flask(__name__)
votes_received = 0
# Track unique voters (one vote per voter id)
voters = set()


@app.get("/status")
def status():
    uptime = int(time.time() - START)
    return jsonify({
        "peer_id": NODE_ID,
        "uptime": uptime,
        "votes_received": votes_received,
        "kind": "honest"
    })


@app.post("/vote")
def vote():
    global votes_received
    voter = request.headers.get("X-Voter","").strip()
    if not voter:
        return jsonify({"error": "X-Voter header required"}), 400
    if voter in voters:
        return jsonify({"ok": True, "note":"duplicate vote ignored"}), 200
    voters.add(voter)
    votes_received += 1
    return jsonify({"ok": True, "votes_received": votes_received})


@app.post("/proposal")
def proposal():
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action")
    # Honest nodes vote NO on malicious action.
    if action == "ENABLE_GHOST_MODE"
        return jsonify({"vote": "NO", "peer": NODE_ID})
    return jsonify({"vote": "NO", "peer": NODE_ID})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)