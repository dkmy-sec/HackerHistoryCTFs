#!/usr/bin/env python3
import os, zipfile, hashlib
ROOT = os.path.join(os.path.dirname(__file__), "..")
packs_dir = os.path.join(ROOT, "data", "files-core", "share", "garbage", "packs")
os.makedirs(packs_dir, exist_ok=True)
png_bytes = bytes([0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x06,0x00,0x00,0x00,0x1F,0x15,0xC4,0x89,0x00,0x00,0x00,0x0A,0x49,0x44,0x41,0x54,0x78,0x9C,0x63,0x00,0x01,0x00,0x00,0x05,0x00,0x01,0x0D,0x0A,0x2D,0xB4,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,0x42,0x60,0x82])
zip_path = os.path.join(packs_dir, "payload.zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for i in range(3):
        name = f"chunks/{i:03d}.bin"
        data = (f"CHUNK {i}\n").encode() * (1024 + i*100)
        z.writestr(name, data)
    index_csv = "slice,offset,length,sha256\n"
    for i in range(3):
        chunkdata = (f"CHUNK {i}\n").encode() * (1024 + i*100)
        sha = hashlib.sha256(chunkdata).hexdigest()
        index_csv += f"{i:03d}.bin,NA,{len(chunkdata)},{sha}\n"
    index_csv += "flag_hint,NA,NA,WWF{TRUST_BUT_VERIFY}\n"
    z.writestr("chunks/index.csv", index_csv)
    confession = "CONFESSION: secadmin used Jenkins job index_garbage to stage artifacts to .stow\nFINAL_FLAG: WWF{HACK_THE_PLANET}\n"
    z.writestr("worm_core.txt", confession)
with open(os.path.join(packs_dir, "pack_0420.png"), "wb") as outf:
    outf.write(png_bytes)
    with open(zip_path, "rb") as zf:
        outf.write(zf.read())
print("Created polyglot at", os.path.join(packs_dir, "pack_0420.png"))