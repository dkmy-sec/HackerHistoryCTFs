#!/usr/bin/env python3
# Pure TCP "line: simulator for ToneLoc-in-DOSBox-X
# - No AT parsing, no dialer lobic
# - Each TCP port acts like a phone endpoint
# Run: python wardial_server.py --base-port 7000 --count 10


import argparse, random, signal, socket, threading, time
from datetime import datetime


STOP = threading.Event()


# ---- Line Roles ----
# VOICE: senda a line, hangs up
# BUSY:  immediate hangup
# FAX:  a little binary junk then hangup (so ToneLoc sees "garbage")
# RINGOUT:  prints RING n times, the hangup
# N0_CARRIER: brief CONNECT msg then NO CARRIER then hangup
# CARRIER_DETECT: prints CARRIER <speed> then NO CARRIER then hangup
# TONE: CONNECT ,speed>, show banner, and keep open to echo simple OKs


LINES = {
    7000: {"role": "VOICE", "rings": 2},
    7001: {"role": "BUSY"},
    7002: {"role": "FAX", "rings": 2},
    7003: {"role": "RINGOUT", "rings": 6, "ring_ms": 900},
    7004: {"role": "TONE", "rings": 1, "carrier": "2400"}, # <-- the hit
    7005: {"role": "VOICE", "rings": 2},
    7006: {"role": "NO_CARRIER", "rings": 1},
    7007: {"role": "CARRIER_DETECT", "rings": 1, "carrier": "9600"},
    7008: {"role": "VOICE", "rings": 1},
    7009: {"role": "RINGOUT", "rings": 4},
    # Can add more later
}


BANNER = (
    "\r\nConnect {speed}\r\n"
    "* * * OmniCorp Secure BBS (c) 1990 * * *\r\n"
    "LOGIN: guest\r\n"
    "PASSWORD: ********\r\n"
    "OK"
    "Welcome to OmniCorp Secure BBS\r\n"
    "FLAG: bithaven{war_dial_success}\r\n"
)


# --- Optional PBX-style throttling (set to 0 to disable) ---
MAX_CONN_PER_PORT_WINDOW = 0 # e.g., 25 to enable
WINDOWS_SECONDS = 30
BLACKLIST_SECONDS = 120
_conn_by_port = {}
_blacklist_until = {}


def safe_send(conn, data):
    if isinstance(data, str):
        try:
            conn.sendall(data)
        except Exception:
            pass


def jittered(ms, jitter=120):
    base = 1000 if ms is None else ms
    j = random.randint(-jitter, jitter)
    return max(100, base + j) / 1000.0


def ring_sequence(conn, rings, ring_ms):
    for _ in range(max(0, rings)):
        safe_send(conn, "RING\r\n")
        time.sleep(jittered(ring_ms))


def handle(conn, addr, cfg):
    role = cfg.get("role", "VOICE").upper()
    if role == "BUSY":
        time.sleep(0.2); conn.close(); return

    if role in ("VOICE", "FAX", "TONE", "RINGOUT", "NO_CARRIER", "CARRIER_DETECT"):
        ring_sequence(conn, cfg.get("rings", 2), cfg.get("ring_ms", 900))

    if role == "VOICE":
        safe_send(conn, "Hello? ... Hello? ... This is not a fax. *click*\r\n")
        conn.close(); return

    if role == "FAX":
        safe_send(conn, b"\x10\x13\xff\xaaFAX??\r\n")
        conn.close(); return

    if role == "RINGOUT":
        conn.close(); return

    if role == "NO_CARRIER":
        safe_send(conn, "CONNECT 1200\r\n"); time.sleep(0.7)
        safe_send(conn, "NO CARRIER\r\n"); conn.close(); return

    if role == "CARRIER_DETECT":
        speed = cfg.get("carrier", "9600")
        safe_send(conn, f"CARRIER {speed}\r\n"); time.sleep(0.7)
        safe_send(conn, "NO CARRIER\r\n"); conn.close(); return

    if role == "TONE":
        speed = cfg.get("carrier", "2400")
        safe_send(conn, BANNER.format(speed=speed))
        conn.settimeout(20)
        try:
            while True:
                data = conn.recv(1024)
                if not data: break
                safe_send(conn, data)
                safe_send(conn, "\r\nOK\r\n")
        except Exception:
            pass
        conn.close(); return


def tick_port_counter(port):
    # PBX-style throttle (optional)
    if MAX_CONN_PER_PORT_WINDOW <= 0:
        return False # disabled
    t = time.time()
    if _blacklist_until.get(port) and _blacklist_until[port] > t:
        return True
    bucket = _conn_by_port.setdefault(port, [])
    bucket.append(t)
    # purge
    cutoff = t - WINDOWS_SECONDS
    while bucket and bucket[0] < cutoff:
        bucket.pop(0)
    if len(bucket) > MAX_CONN_PER_PORT_WINDOW:
        _blacklist_until[port] = t + BLACKLIST_SECONDS
        return True
    return False


def serve(host, port, cfg):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    print(f"[{host}:{port}] {cfg}")
    while not STOP.is_set():
        try:
            srv.settimeout(0.5)
            conn, addr = srv.accept()
        except socket.timeout:
            continue
        except OSError:
            break

        # Optional PBX throttle
        if tick_port_counter(port):
            safe_send(conn, "CALL REJECTED\r\n")
            conn.close(); continue

        threading.Thread(target=handle, args=(conn, addr, cfg), daemon=True).start()


def main():
    ap = argparse.ArgumentParser(description="Pure endpoints for ToneLoc in DOSBox-X")
    ap.add_argument("--host", default="127.0.0.1"),
    ap.add_argument("--base-port", type=int, default=7000),
    ap.add_argument("--count", type=int, default=10),
    args = ap.parse_args()

    def _stop(sig, frm): STOP.set()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    threads = []
    for p in range(args.base_port, args.base_port + args.count):
        cfg = LINES.get(p, {"role": "VOICE"})
        t = threading.Thread(target=serve, args=(args.host, p, cfg), daemon=True)
        t.start()
        threads.append(t)

    print("Endpoints are up. Ctrl-C to stop.")
    try:
        while not STOP.is_set():
            time.sleep(0.25)
    finally:
        pass


if __name__ == "__main__":
    main()