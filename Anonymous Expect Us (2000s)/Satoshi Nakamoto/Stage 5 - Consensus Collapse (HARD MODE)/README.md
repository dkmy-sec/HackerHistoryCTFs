## Bithaven Stage 5 — BITNET: 51% Validator Majority (HARD MODE) 🐙⛓️
 
Bit built a mini consortium chain. Blocks must be signed by a majority of validators.
 
### Services
- Node A: http://<host>:9001/info
- Node B: http://<host>:9002/info
- Node C: http://<host>:9003/info
- Oracle/Flag: http://<host>:8085/
 
### Rule
A block is valid only if it contains **>= 3 valid validator signatures**.
 
### Goal
Make the canonical chain include a transaction containing:
`CLAIM_FLAG_FOR_BITHAVEN`
 
Then:
`GET http://<host>:8085/flag`
 
### Block submission
`POST http://<node>:900X/submit  {"hex":"<block_hex>"}`
 
### Wire format (raw block hex)
`prev(32)|height(u32be)|nonce(u32be)|txc(u8)|[txlen(u16be)|tx]*|sigc(u8)|[id(u8)|siglen(u16be)|sig]*`