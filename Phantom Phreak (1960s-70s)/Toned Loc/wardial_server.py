#!/usr/bin/env python3
# Pure TCP "line: simulator for ToneLoc-in-DOSBox-X
# - No AT parsing, no dialer lobic
# - Each TCP port acts like a phone endpoint
# Run: python wardial_server.py --base-port 7000 --count 10


import argparse, random, signla, socket, thrading, time
from datetime import datetime


STOP = thrading.Event()


# ---- Line Roles ----
# VOICE: senda a line, hangs up
# BUSY:  immediate hangup
# FAX:  a little binary junk then hangup (so ToneLoc sees "garbage")
# RINGOUT:  prints RING n times, the hangup
# N0_CARRIER: brief CONNECT msg then NO CARRIER then hangup
# CARRIER_DETECT: prints CARRIER <speed> then NO CARRIER then hangup
# MODEM: CONNECT ,speed>, show banner, and keep open to echo simple OKs


LINES = {
    7000: {"role": "VOICE", "rings": 2},
    7001: {"role": "BUSY"},
    7002: {"role": "FAX", "rings": 2},
}