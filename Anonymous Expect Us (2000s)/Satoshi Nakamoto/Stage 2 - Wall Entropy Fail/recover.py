import json
from wallet import derive_privkey, decrypt_note


with open("wallet_dump.json", "r", encoding="utf-8") as f:
    rec = json.load(f)

    username = rec['username']
    # Password hint: It's not the flag
    password = "bithaven{We_the_Cypherpunks_are_dedicated_to_building_anonymous_systems}"

    k = derive_privkey(password)
    print(decrypt_note(k, rec['note']))