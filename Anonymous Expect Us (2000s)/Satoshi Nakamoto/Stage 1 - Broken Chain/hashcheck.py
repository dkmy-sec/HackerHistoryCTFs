import json, hashlib


def bit_hash(block: dict) -> str:
    # Bit forgot to include prev_hash and any real PoW rules
    s = f"{block['index']}{block['data']}{block['nonce']}"
    return hashlib.sha256(s.encode()).hexdigest()

with open("bitchain.json", "r", encoding="utf-8") as f:
    chain = json.load(f)

    bad = []
    for b in chain:
        calc = bit_hash(b)
        if calc != b["hash"]:
            bad.append((b['index'], b['hash'], calc))

    if bad:
        print("[!] Hash mismatches found:")
        for idx, old, calc in bad:
            print(f"Block {idx}: file={old} calc={calc}")
    else:
        print("[+] All hashes match (suspiciously).")