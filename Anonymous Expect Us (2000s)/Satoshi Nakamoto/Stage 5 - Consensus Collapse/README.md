## Bithaven Stage 5 — BITNET: Consensus Collapse (HARD MODE) 🐙⛓️
 
Bit built a 3-node cypherpunk network called BITNET.
The nodes sync blocks and choose the “best chain” by total work.
 
### Services
- Node A: http://<host>:9001/info
- Node B: http://<host>:9002/info
- Node C: http://<host>:9003/info
- Flag oracle: http://<host>:8085/
 
### Goal
Make the network accept YOUR chain as the best chain, and include a transaction containing:
`CLAIM_FLAG_FOR_BITHAVEN`
 
When you think you won, fetch:
`GET http://<host>:8085/flag`
 
### Block submission
POST a raw block as hex to any node:
`POST /submit  {"hex":"<block_hex>"}`
 
### Wire format
`prev(32)|height(u32be)|work(u64be)|nonce(u32be)|txc(u8)|[txlen(u16be)|tx...]`

