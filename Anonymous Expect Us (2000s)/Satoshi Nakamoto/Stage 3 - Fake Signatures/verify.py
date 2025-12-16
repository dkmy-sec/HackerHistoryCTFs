import json, hashlib


def verify(tx: dict) -> bool:
    # Bit thinks "signature == sha256(message)" is a signature 🤡
    msg = f"{tx['from']}|{tx['to']}|{tx['amount']}|{tx['memo','']}"
    sig = hashlib.sha256(msg.encode()).hexdigest()
    return sig == tx['signature']

if __name__ == "__main__":
    tx = json.load(open("signed_tx.json", "r", encoding="utf-8"))
    if verify(tx):
        print("[+] Transmission verified.")
    else:
        print("[-] Invalid signature.")