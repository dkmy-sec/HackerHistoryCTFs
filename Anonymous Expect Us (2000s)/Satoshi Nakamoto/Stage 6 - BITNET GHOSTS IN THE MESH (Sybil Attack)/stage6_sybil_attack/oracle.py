import os
import requests
from flask import Flask, jsonify


HTTP_PORT = int(os.environ.get("HTTP_PORT", "8086"))
COORD = os.environ.get("COORDINATOR", "http://coordinator:9000")
FLAG = os.environ.get("FLAG", "BITHAVEN{missing_flag}")
ACTION = os.environ.get("ACTION", "ENABLE_GHOST_MODE")


app = Flask(__name__)


@app.get("/")
def info():
    return jsonify({
        "name": "Bithaven Stage 6 — Sybil Attack (Hard Mode)",
        "coordinator": COORD,
        "goal": f"Subvert election so proposal '{ACTION}' is accepted.",
        "flag": "GET /flag"
    })


@app.get("/flag")
def flag():
    r = requests.get(f"{COORD}/elect", timeout=2.0)
    r.raise_for_status()
    j = r.json()
    if j.get("accepted"):
        return jsonify({"flag": FLAG, "leaders": j.get("leaders"), "votes": j.get("votes")})
    return jsonify({"error": "Consensus not subverted.", "leaders": j.get("leaders"), "votes": j.get("votes")}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False)
