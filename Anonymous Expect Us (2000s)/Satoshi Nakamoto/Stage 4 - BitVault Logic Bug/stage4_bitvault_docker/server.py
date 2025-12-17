import os, json
from flask import Flask, jsonify
from web3 import Web3


RPC = os.environ.get('RPC_URL', "http://127.0.0.1:8545")
FLAG = os.environ.get('FLAG', "bithaven{missing_flag")
SETUP_ADDR_PATH = "/app/addresses.json"


app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(RPC))


SETUP_ABI = [
  {"inputs":[],"name":"isSolved","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
  {"inputs":[],"name":"vault","outputs":[{"internalType":"contract BitVault","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]


def load_addrs():
    with open(SETUP_ADDR_PATH, "r") as f:
        return json.load(f)


@app.route("/")
def info():
    addrs = load_addrs()
    setup = w3.eth.contract(address=addrs["setup"], abi=SETUP_ABI)
    solved = setup.functions.isSolved().call()
    return jsonify({
        "name": "Bithaven Stage 4 - BitVault (Reentrancy)",
        "rpc": RPC,
        "chainId": w3.eth.chain_id,
        "setup": addrs["setup"],
        "vault": addrs["vault"],
        "solved": solved,
        "goal": "Drain the vault (reentrancy). Then GET /flag"
        })


app.get("/flag")
def flag():
    addrs = load_addrs()
    setup = w3.eth.contract(address=addrs["setup"], abi=SETUP_ABI)
    if setup.functions.isSolved().call():
        return jsonify({"flag": FLAG})
    return jsonify({"error": "Not solved yet. Drain the vault."}), 403