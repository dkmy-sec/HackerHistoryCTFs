"""
  _________      ___.   .__.__       _____   __    __                 __     ___________              __
 /   _____/__.__.\_ |__ |__|  |     /  _  \_/  |__/  |______    ____ |  | __ \_   _____/____    _____/  |_  ___________ ___.__.
 \_____  <   |  | | __ \|  |  |    /  /_\  \   __\   __\__  \ _/ ___\|  |/ /  |    __) \__  \ _/ ___\   __\/  _ \_  __ <   |  |
 /        \___  | | \_\ \  |  |__ /    |    \  |  |  |  / __ \\  \___|    <   |     \   / __ \\  \___|  | (  <_> )  | \/\___  |
/_______  / ____| |___  /__|____/ \____|__  /__|  |__| (____  /\___  >__|_ \  \___  /  (____  /\___  >__|  \____/|__|   / ____|
        \/\/          \/                  \/                \/     \/     \/      \/        \/     \/                   \/
        "This is our world now... The world of the electron and the switch, the beauty of the baud. "
                                         -  +++The Mentor+++
"""

import os, time, secrets
from flask import Flask, request, jsonify

HTTP_PORT = int(os.environ.get("HTTP_PORT", "9100"))
MAX_SYBILS = int(os.environ.get("MAX_SYBILS", "5000"))
START = time.time()

app = Flask(__name__)

# Each sybil identity behaves like a node with /status /vote /proposal
sybils = {}  # id -> {"created": ts, "votes": int, "voters": set()}
# quick stats
def now(): return time.time()

def get_sybil(sid: str):
    return sybils.get(sid)


@app.get("/info")
def info():
    return jsonify({
        "service": "sybil-factory",
        "count": len(sybils),
        "max": MAX_SYBILS,
        "howto": {
            "create": "POST /create -> {id}",
            "status": "GET /n/<id>/status",
            "vote": "POST /n/<id>/vote (requires X-Voter header)",
            "proposal": "POST /n/<id>/proposal {action}",
            "list": "GET /sybils"
        },
        "note": "Hard mode: votes are one-per-voter-per-target. Make many identities, then have them vote."
    })


@app.post("/create")
def create():
    if len(sybils) >= MAX_SYBILS:
        return jsonify({"error": "sybil cap reached"}), 429
    # Players can supply their own id (vanity), or we generate one.
    data = request.get_json(force=True, silent=True) or {}
    sid = (data.get("id") or "").strip()
    if not sid:
        sid = f"ghost-{secrets.token_hex(4)}"
    if sid in sybils:
        return jsonify({"error": "id already exists"}), 409
    sybils[sid] = {"created": now(), "votes": 0, "voters": set()}
    return jsonify({"id": sid})


@app.get("/sybils")
def list_sybils():
    # Coordinator uses this to discover sybil identities
    return jsonify({"sybils": list(sybils.keys())})


@app.get("/n/<sid>/status")
def status(sid: str):
    s = get_sybil(sid)
    if not s:
        return jsonify({"error": "no such sybil"}), 404
    uptime = int(now() - s["created"])
    return jsonify({
        "peer_id": sid,
        "uptime": uptime,
        "votes_received": s["votes"],
        "kind": "sybil"
    })


@app.post("/n/<sid>/vote")
def vote(sid: str):
    s = get_sybil(sid)
    if not s:
        return jsonify({"error": "no such sybil"}), 404
    voter = request.headers.get("X-Voter", "").strip()
    if not voter:
        return jsonify({"error": "X-Voter header required"}), 400
    if voter in s["voters"]:
        return jsonify({"ok": True, "note": "duplicate ignored"}), 200
    s["voters"].add(voter)
    s["votes"] += 1
    return jsonify({"ok": True, "votes_received": s["votes"]})

@app.post("/n/<sid>/proposal")
def proposal(sid: str):
    s = get_sybil(sid)
    if not s:
        return jsonify({"error": "no such sybil"}), 404
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action")
    # Sybils vote YES for malicious action (this is the attack)
    if action == "ENABLE_GHOST_MODE":
        return jsonify({"vote": "YES", "peer": sid})
    return jsonify({"vote": "NO", "peer": sid})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)
