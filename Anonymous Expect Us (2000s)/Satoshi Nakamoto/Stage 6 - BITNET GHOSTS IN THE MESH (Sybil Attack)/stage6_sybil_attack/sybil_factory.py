"""
  _________      ___.   .__.__       _____   __    __                 __     ___________              __
 /   _____/__.__.\_ |__ |__|  |     /  _  \_/  |__/  |______    ____ |  | __ \_   _____/____    _____/  |_  ___________ ___.__.
 \_____  <   |  | | __ \|  |  |    /  /_\  \   __\   __\__  \ _/ ___\|  |/ /  |    __) \__  \ _/ ___\   __\/  _ \_  __ <   |  |
 /        \___  | | \_\ \  |  |__ /    |    \  |  |  |  / __ \\  \___|    <   |     \   / __ \\  \___|  | (  <_> )  | \/\___  |
/_______  / ____| |___  /__|____/ \____|__  /__|  |__| (____  /\___  >__|_ \  \___  /  (____  /\___  >__|  \____/|__|   / ____|
        \/\/          \/                  \/                \/     \/     \/      \/        \/     \/                   \/
        "This is our world now... The world of the electron and the switch, the beauty of the baud. "
                                         -  +++The Mentor+++
"""

import os, time, secrets
from flask import Flask, request, jsonify


HTTP_PORT = int(os.environ.get("HTTP_PORT", "9100"))
MAX_SYBILS = int(os.environ.get("MAX_SYBILS", "5000"))
START = time.time()


app = Flask(__name__)


# Each sybil identity behaves like a noe with /status /vote /proposal
sybils = {}