"""
 d8b        d8,                                  d8b  d8b
 ?88       `8P    d8P                            88P  88P           d8P
  88b          d888888P                         d88  d88         d888888P
  888888b   88b  ?88'   ?88   d8P  d8P d888b8b  888  888   d8888b  ?88'
  88P `?8b  88P  88P    d88  d8P' d8P'd8P' ?88  ?88  ?88  d8b_,dP  88P
 d88,  d88 d88   88b    ?8b ,88b ,88' 88b  ,88b  88b  88b 88b      88b
d88'`?88P'd88'   `?8b   `?888P'888P'  `?88P'`88b  88b  88b`?888P'  `?8b

'The Times 03/Jan/2009 Chancellor on Brink of Second Bailout for Banks. ' - Satoshi Nakamoto
"""

import hashlib


def derive_privkey(username: str, password: str) -> str:
    # Bit uses predicatable key derivation (don't do this)
    h = hashlib.sha256(username + ":" + password).encode().digest()
    return h # 32 bytes


def xor_byets(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt(note: str, privkey: bytes) -> str:
    # XOR not with privkey (first N bytes).  Bit thinks this is encryption.  Bit has a lot to learn.
    pt = note.encode()
    ct = xor_bytes(pt, privkey[:len(pt)])
    return ct.hex()


def decrypt_note(note_hex: str, privkey: bytes) -> str:
    ct = bytes.fromhex(note_hex)
    pt = xor_bytes(ct, privkey[:len(ct)])
    return pt.decode(errors="replace")