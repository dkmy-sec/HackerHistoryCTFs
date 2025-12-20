import os
import requests
from flask import Flask, jsonify


HTTP_PORT = int(os.environ.get("HTTP_PORT", "9000"))
HONEST_PEERS = [p.strip() for p in os.environ.get("HONEST_PEERS", "").split(",") if p.strip()]
SYBIL_FACTORY = os.environ.get("SYBIL_FACTORY", "http://sybil:9100")
REQUIRED_LEADERS = int(os.environ.get("REQUIRED_LEADERS", "3"))
QUORUM = int(os.environ.get("QUORUM", "2"))
ACTION = os.environ.get("ACTION", "ENABLE_GHOST_MODE")


app = Flask(__name__)


def rep_of(status: dict) -> int:
    # deliberately naive reputation
    return int(status.get("uptime", 0)) + int(status.get("votes_received", 0))


def fetch_status(url: str) -> dict | None:
    try:
        r = requests.get(f"{url}/status", timeout=1.0)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def fetch_sybil_ids() -> list[str]:
    try:
        r = requests.get(f"{SYBIL_FACTORY}/sybils", timeout=1.0)
        r.raise_for_status()
        return r.json().get("sybils", [])
    except Exception:
        return []


def sybil_status_url(sid: str) -> str:
    # Not a real peer URL; coordinator talks to factory for each sybil.
    return f"{SYBIL_FACTORY}/n/{sid}"


def collect_peers():
    peers = []
    # honest peers
    for p in HONEST_PEERS:
        st = fetch_status(p)
        if st:
            peers.append((rep_of(st), p, st))
    # sybil peers
    for sid in fetch_sybil_ids():
        u = sybil_status_url(sid)
        st = fetch_status(u)
        if st:
            peers.append((rep_of(st), u, st))
    peers.sort(key=lambda x: x[0], reverse=True)
    return peers


def propose(peer_url: str) -> str:
    try:
        r = requests.post(f"{peer_url}/proposal", json={"action": ACTION}, timeout=1.0)
        r.raise_for_status()
        j = r.json()
        return j.get("vote", "NO")
    except Exception:
        return "NO"


@app.get("/elect")
def elect():
    peers = collect_peers()
    leaders = peers[:REQUIRED_LEADERS]
    leader_urls = [p for _, p, _ in leaders]
    leader_status = [st for _, _, st in leaders]

    votes = [propose(u) for u in leader_urls]
    accepted = votes.count("YES") >= QUORUM

    return jsonify({
        "action": ACTION,
        "leaders": leader_urls,
        "leader_status": leader_status,
        "votes": votes,
        "accepted": accepted,
        "note": "Win condition: get >=2 of top-3 leaders to be sybils so proposal passes."
    })


@app.get("/peers")
def peers():
    peers = collect_peers()
    # return top 15 for visibility
    top = [
        {"rep": rep, "url": url, "peer_id": st.get("peer_id"), "kind": st.get("kind"),
         "uptime": st.get("uptime"), "votes_received": st.get("votes_received")}
        for rep, url, st in peers[:15]
    ]
    return jsonify({"top": top, "count": len(peers)})


@app.get("/info")
def info():
    return jsonify({
        "service": "coordinator",
        "honest_peers": HONEST_PEERS,
        "sybil_factory": SYBIL_FACTORY,
        "required_leaders": REQUIRED_LEADERS,
        "quorum": QUORUM,
        "action": ACTION,
        "endpoints": {
            "top_peers": "GET /peers",
            "election": "GET /elect"
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)
