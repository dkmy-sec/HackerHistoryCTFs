#!/usr/bin/env python3
# gen_phonebook.py — make DOSBox-X modem phonebook mappings
# Example:
#   python gen_phonebook.py --npa 212 --nxx 555 --start 1200 --end 1209 --host localhost --base-port 7000 > phonebook.txt
# Or using a template:
#   python gen_phonebook.py --template 21255512?? --range 00 09 --host localhost --base-port 7000 > phonebook.txt

import argparse

def main():
    ap = argparse.ArgumentParser(description="Generate DOSBox-X phonebook mappings")
    g1 = ap.add_argument_group("Standard range")
    g1.add_argument("--npa", type=int, help="Area code, e.g., 212")
    g1.add_argument("--nxx", type=int, help="Exchange, e.g., 555")
    g1.add_argument("--start", type=int, help="Line start, e.g., 1200")
    g1.add_argument("--end", type=int, help="Line end, e.g., 1209")

    g2 = ap.add_argument_group("Template range")
    g2.add_argument("--template", help="Number template with ?? for range, e.g., 21255512??")
    g2.add_argument("--range", nargs=2, metavar=("FROM","TO"), help="Inclusive 2-digit range, e.g., 00 09")

    ap.add_argument("--host", default="localhost")
    ap.add_argument("--base-port", type=int, default=7000, help="Starting port (increments by 1)")
    args = ap.parse_args()

    entries = []
    if args.template and args.range:
        frm, to = args.range
        if not (len(frm)==2 and len(to)==2):
            raise SystemExit("Range must be two digits, e.g., 00 09")
        lo, hi = int(frm), int(to)
        idx = 0
        for i in range(lo, hi+1):
            num = args.template.replace("??", f"{i:02d}")
            port = args.base_port + idx
            entries.append((num, f"{args.host}:{port}"))
            idx += 1
    else:
        if None in (args.npa, args.nxx, args.start, args.end):
            raise SystemExit("Provide either (npa,nxx,start,end) OR (template,range).")
        idx = 0
        for line in range(args.start, args.end+1):
            num = f"{args.npa}{args.nxx}{line:04d}"
            port = args.base_port + idx
            entries.append((num, f"{args.host}:{port}"))
            idx += 1

    for num, target in entries:
        print(f"{num} {target}")

if __name__ == "__main__":
    main()
