# arpanet_login.py
import socket, threading, base64
import os


BANNER = ("SRI-ARC IMP 1969\nLOGIN: ")
PORT = int(os.getenv("PORT", 1969))
# === Obfuscated flag bits (built by a tiny builder; see below) ===
# plaintext -> XOR with 0x37 -> base85
_KEY = 0x37
_BLOB = b'<F/%"<^BVd9NtV4>?F^.=_L2i<)ca`6qR'

def _reveal():
    raw = base64.a85decode(_BLOB)
    # XOR with single-byte key
    out = bytes(b ^ _KEY for b in raw).decode('utf-8')
    return out

def handler(conn):
    try:
        conn.sendall(BANNER.encode())
        data = conn.recv(1024).decode(errors='ignore').strip().lower()

        # Historically 'lo' sent before crash. Accept 'lo' as magic.
        if data == 'lo':
            flag = _reveal()          # flag only exists here
            try:
                conn.sendall((f"SYSTEM: ACCEPTED.\nFLAG:{flag}\n").encode())
            finally:
                # scrub best-effort (Python strings are immutable, but drop refs)
                del flag
        else:
            conn.sendall(b"SYSTEM: CRASHED\n")
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()

if __name__ == "__main__":
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT)); s.listen(25)
    print(f"[+] ARPANET sim on {PORT}/tcp")
    while True:
        c, _ = s.accept()
        threading.Thread(target=handler, args=(c,), daemon=True).start()
