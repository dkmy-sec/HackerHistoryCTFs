#!/usr/bin/env python3
import os, json
ROOT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(ROOT, exist_ok=True)
out = os.path.join(ROOT, "logs.txt")
events = [
    {"ts":"2025-10-01T09:05:00Z","host":"jenkins","actor":"secadmin","action":"started_job","job":"index_garbage","note":"artifact upload to /share/garbage/.stow"},
    {"ts":"2025-10-01T09:05:12Z","host":"files-core","actor":"secadmin","action":"smb_write","path":"/share/garbage/.stow/loader.sh","note":"uploader"}
]
with open(out,"w") as f:
    for e in events:
        f.write(json.dumps(e) + "\n")
print(f"Wrote {len(events)} seed log events to {out}")