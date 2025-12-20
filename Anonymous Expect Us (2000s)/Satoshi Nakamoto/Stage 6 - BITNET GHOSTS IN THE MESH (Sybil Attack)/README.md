## Bithaven Stage 6 — Sybil Attack: Ghosts in the Mesh 🐙👻

Bit built a “reputation-based” network. Leader election is based on:
`reputation = uptime + votes_received`

Top 3 leaders vote on a proposal. If **2 of 3** vote YES, the proposal passes.

Honest nodes vote **NO**.
Sybil identities vote **YES**.

### Services
- Sybil Factory (create identities): `http://<host>:9100/info`
- Coordinator (election + leaderboard): `http://<host>:9000/info`
- Oracle/Flag: `http://<host>:8086/`

### Goal
Create enough Sybil identities, and use them to vote each other up so that **>= 2 of the Top-3 leaders are Sybils**.
Then claim the flag:
`GET http://<host>:8086/flag`

### How to Sybil
1) Create many identities:
`POST http://<host>:9100/create  {"id":"ghost-001"}`

2) Vote for a target identity (one vote per voter per target):
`POST http://<host>:9100/n/<target>/vote`
with header:
`X-Voter: <your_voter_id>`

Use your Sybil identities as unique voters to farm votes.

See leaderboards:
`GET http://<host>:9000/peers`
