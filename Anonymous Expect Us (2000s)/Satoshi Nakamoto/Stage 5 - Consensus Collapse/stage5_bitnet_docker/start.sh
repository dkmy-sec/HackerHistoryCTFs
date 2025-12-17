#!/usr/bin/env bash
set -euo pipefail

if [[ "${NODE_ID:-}" != ""]]; then
  python3 /app/node.py
else
  exec "$@"
fi