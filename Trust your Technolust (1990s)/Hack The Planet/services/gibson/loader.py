#!/usr/bin/env python3
import zipfile, tempfile, sys, os
def extract_zip_from_polyglot(path):
    with open(path, "rb") as f:
        data = f.read()
    idx = data.find(b"PK\x03\x04")
    if idx == -1:
        raise RuntimeError("No ZIP found in polyglot")
    return data[idx:]
def main(poly_path):
    zdata = extract_zip_from_polyglot(poly_path)
    with tempfile.TemporaryDirectory() as td:
        zip_path = os.path.join(td, "payload.zip")
        with open(zip_path, "wb") as zf:
            zf.write(zdata)
        with zipfile.ZipFile(zip_path, "r") as z:
            print("ZIP contents:")
            for n in z.namelist():
                print(" -", n)
            if "worm_core.txt" in z.namelist():
                with z.open("worm_core.txt") as wf:
                    content = wf.read().decode(errors="replace")
                    print("\n===== CONFESSION & FLAG =====\n")
                    print(content)
            else:
                print("worm_core.txt not found.")
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: loader.py <polyglot.png>")
        sys.exit(1)
    main(sys.argv[1])
