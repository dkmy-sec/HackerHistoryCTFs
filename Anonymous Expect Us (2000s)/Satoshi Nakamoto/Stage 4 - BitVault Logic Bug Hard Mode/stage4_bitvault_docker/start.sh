#!/usr/bin/env bash
set -euo pipfail

# ---- Config ----
export RPC_URL="http://127.0.0.1:8545"

# Fixed private key for deployer (anvil account[0])
# NOTE: This is fine for CTF. Players should use their own wallets/accounts.
export DEPLOYER_KEY="0x59c6995e998f97a5a0044966f094538e7eecf2b2a2a4b6d2e7d6b5a7b6d2c0b7"
export DEPLOYER_PRIV="$DEPLOYER_KEY"

VAULT_ETH="${VAULT_ETH:-10}"
export VAULT_WEI=$(python3 - <<PY
from decimal import Decimal
import os
eth = Decimal(os.environ["VAULT_ETH"])
wei = int(eth * Decimal(10**18))
print(wei)
PY
)

# ---- Start chain ----
# anvil provides JSON-RPC on 8545
anvil --host 0.0.0.0 --port 8545 --chain-id 31337 --silent &
ANVIL_PID=$!

# wait for rpc
python3 - <<'PY'
import time, requests
url="http://127.0.0.1:8545"
for _ in range(60):
    try:
        r=requests.post(url,json={"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1},timeout=0.5)
        if r.status_code==200:
            print("RPC ready")
            break
    except Exception:
        pass
    time.sleep(0.25)
else:
    raise SystemExit("RPC not ready")
PY

# ---- Deploy contracts ----
forge script script/Deploy.s.sol:Deploy --rpc-url http://127.0.0.1:8545 --broadcast > /tmp/deploy.log

SETUP=$(grep "SETUP_ADDRESS" /tmp/deploy.log | tail -1 | awk '{print $2}')
VAULT=$(grep "VAULT_ADDRESS" /tmp/deploy.log | tail -1 | awk '{print $2}')

echo "{\"setup\":\"$SETUP\",\"vault\":\"$VAULT\"}" > /app/addresses.json
echo "[+] Deployed Setup: $SETUP"
echo "[+] Deployed Vault: $VAULT"

# ---- Start web server ----
python3 /app/server.py --host 0.0.0.0 --port 8080 &

# keep container alive, forward signals
wait $ANVIL_PID