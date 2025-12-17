import os, json, time
from flask import Flask, jsonify, request
from web3 import Web3

RPC = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
FLAG = os.environ.get("FLAG", "BITHAVEN{missing_flag}")
ADDR_PATH = "/app/addresses.json"

# Anvil account[0] private key used by start.sh deployer
DEPLOYER_PRIV = os.environ.get(
    "DEPLOYER_PRIV",
    "0x59c6995e998f97a5a0044966f094538e7eecf2b2a2a4b6d2e7d6b5a7b6d2c0b7"
)

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(RPC))

# Minimal ABI for server-side checks only
SETUP_ABI = [
    {"inputs": [], "name": "isSolved", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "vault", "outputs": [{"internalType": "address", "name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"}
]

RATE = {}  # naive rate limiter: ip -> last_ts


def load_addrs():
    with open(ADDR_PATH, "r") as f:
        return json.load(f)


@app.get("/")
def info():
    addrs = load_addrs()
    return jsonify({
        "name": "Bithaven Stage 4 — BitVault (HARD MODE)",
        "rpc": RPC,
        "chainId": w3.eth.chain_id,
        "setup": addrs["setup"],
        "notes": [
            "Hard mode: Vault address is not given. Discover it by calling Setup.vault() via raw calldata.",
            "Hard mode: withdraw is CONTRACT-ONLY (EOAs blocked). You must deploy an attacker contract."
        ],
        "selectors": {
            "deposit()": "0xd0e30db0",
            "withdraw(uint256)": "0x2e1a7d4d",
            "vault()": "0xfbfa77cf",
            "isSolved()": "0x64d98f6e"
        },
        "endpoints": {
            "faucet": "GET /faucet?to=0xYourAddress (1 ETH, rate-limited)",
            "flag": "GET /flag (only after drain condition)"
        }
    })


@app.get("/status")
def status():
    addrs = load_addrs()
    setup = w3.eth.contract(address=addrs["setup"], abi=SETUP_ABI)
    solved = setup.functions.isSolved().call()
    # server can read vault address for status display, but we still don't give it on /
    vault_addr = setup.functions.vault().call()
    bal = w3.eth.get_balance(vault_addr)
    return jsonify({
        "solved": solved,
        "vaultBalanceWei": str(bal),
        "vaultBalanceEthApprox": float(bal) / 1e18
    })


@app.get("/faucet")
def faucet():
    to = request.args.get("to", "").strip()
    if not (to and w3.is_address(to)):
        return jsonify({"error": "usage: /faucet?to=0xYourAddress"}), 400

    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
    now = time.time()
    last = RATE.get(ip, 0)
    if now - last < 20:  # 20s cooldown
        return jsonify({"error": "rate limited. try again soon."}), 429
    RATE[ip] = now

    acct = w3.eth.account.from_key(DEPLOYER_PRIV)
    tx = {
        "from": acct.address,
        "to": Web3.to_checksum_address(to),
        "value": w3.to_wei(1, "ether"),
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    }
    signed = acct.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.rawTransaction)
    return jsonify({"sent": "1 ETH", "to": to, "txHash": txh.hex()})


@app.get("/flag")
def flag():
    addrs = load_addrs()
    setup = w3.eth.contract(address=addrs["setup"], abi=SETUP_ABI)
    if setup.functions.isSolved().call():
        return jsonify({"flag": FLAG})
    return jsonify({"error": "Not solved yet. Drain the vault."}), 403