#!/usr/bin/env python3
# merge_toneloc_log.py
# Example:
#   python merge_toneloc_log.py --log toneloc.log \
#     --book address_book_template.csv --out address_book_filled.csv
#
# It tries to parse lines like:
#   212-555-1204: CONNECT 2400
#   2125551201: BUSY
#   Dialing 212-555-1208 ... CARRIER 9600
#   212-555-1200: VOICE
#   212-555-1203: NO CARRIER
#
# Columns in book: Number,Observation,Carrier,Notes

import argparse, csv, re

RE_LINE = re.compile(
    r"(?P<num>(?:\d{3}-?\d{3}-?\d{4}))"
    r".*?(?P<obs>CONNECT \d+|CARRIER \d+|NO CARRIER|BUSY|VOICE|FAX|RING(?:ING)?|RINGOUT|CALL REJECTED)",
    re.IGNORECASE
)

def normalize_num(s):
    # "212-555-1204" or "2125551204" -> "212-555-1204"
    d = re.sub(r"\D", "", s)
    return f"{d[0:3]}-{d[3:6]}-{d[6:10]}" if len(d) == 10 else s

def parse_obs(obs):
    obs = obs.upper()
    carrier = ""
    if obs.startswith("CONNECT "):
        carrier = obs.split()[1]
    elif obs.startswith("CARRIER "):
        carrier = obs.split()[1]
    # Normalize for the CSV Observation column
    if obs.startswith("CONNECT "):
        return "CONNECT", carrier
    if obs.startswith("CARRIER "):
        return "CARRIER", carrier
    return obs, carrier

def main():
    ap = argparse.ArgumentParser(description="Merge ToneLoc logs into address book CSV")
    ap.add_argument("--log", required=True, help="Path to ToneLoc log (text)")
    ap.add_argument("--book", required=True, help="Path to address book CSV (template)")
    ap.add_argument("--out", required=True, help="Output CSV")
    args = ap.parse_args()

    # 1) Parse log -> latest observation per number
    latest = {}
    with open(args.log, "r", errors="ignore") as f:
        for line in f:
            m = RE_LINE.search(line)
            if not m:
                continue
            num = normalize_num(m.group("num"))
            obs_raw = m.group("obs")
            obs, carrier = parse_obs(obs_raw)
            latest[num] = {"Observation": obs, "Carrier": carrier, "Notes": ""}

    # 2) Load template and fill rows if we have data
    rows = []
    with open(args.book, newline="") as f:
        rdr = csv.DictReader(f)
        fieldnames = rdr.fieldnames or ["Number","Observation","Carrier","Notes"]
        for r in rdr:
            n = normalize_num(r.get("Number",""))
            if n in latest:
                r["Observation"] = latest[n]["Observation"]
                r["Carrier"] = latest[n]["Carrier"]
                # Leave Notes intact if student already wrote something
            rows.append(r)

    # 3) Write out
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Number","Observation","Carrier","Notes"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Filled address book written to {args.out}")

if __name__ == "__main__":
    main()
