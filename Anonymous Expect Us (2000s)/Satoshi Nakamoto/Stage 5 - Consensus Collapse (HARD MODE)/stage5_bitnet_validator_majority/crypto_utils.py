import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def b2h(b: bytes) -> str:
    return b.hex()


def h2b(h: str) -> bytes:
    return bytes.fromhex(h)


def u32be(x: int) -> bytes:
    return x.to_bytes(4, "big", signed=False)


def pub_from_hex(pub_hex: str) -> Ed25519PublicKey:
    return Ed25519PublicKey.from_public_bytes(
        h2b(pub_hex)
    )


def priv_from_hex(priv_hex: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(
        h2b(priv_hex)
    )


def gen_key_pair() -> tuple[str, str]:
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_hex = priv.private_bytes_raw().hex()
    pub_hex = pub.public_bytes_raw().hex()
    return priv_hex, pub_hex


def sign(priv_hex: str, msg: bytes) -> bytes:
    priv = priv_from_hex(priv_hex)
    return priv.sign(msg)


def verify(pub_hex: str, msg: bytes, sig: bytes) -> bool:
    pub = pub_from_hex(pub_hex)
    try:
        pub.verify(sig, msg)
        return True
    except Exception:
        return False