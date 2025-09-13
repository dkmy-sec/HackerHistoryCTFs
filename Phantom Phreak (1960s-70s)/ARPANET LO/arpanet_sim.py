import socket, threading
FLAG = "bithaven{lo_login_success}"
BANNER = ("SRI-ARC IMP 1969\nLOGIN: ")


def handler(conn):
    conn.sendall(BANNER.encode())
    data = conn.recv(1024).decode(errors='ignore').strip().lower()
    # Historically 'lo' sent before crash. Accept 'lo' as magic.
    if data == 'lo':
        conn.sendall(("SYSTEM: ACCEPTED.\nFLAG:"+FLAG+"\n").encode())
    else:
        conn.sendall(b"SYSTEM: CRASHED\n")
        conn.close()


if __name__ == "__main__":
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind(("0.0.0.0", 1969)); s.listen(25)
    print("[+] ARPANET sim on 1969/tcp")
    while True:
        c,_=s.accept(); threading.Thread(target=handler,args=(c,),daemon=True).start()