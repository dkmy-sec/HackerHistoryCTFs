## Bithaven Stage 4 — BitVault (HARD MODE) 🐙
 
RPC: `http://<host>:8545`  
Info: `http://<host>:8080/`
 
This is a real EVM chain. Bit deployed a vulnerable vault.
 
**Hard Mode rules:**
- The vault address is NOT handed to you.
- `withdraw(uint256)` is CONTRACT-ONLY (EOAs blocked).
- You must craft raw calldata (selectors provided).
- You must deploy an attacker contract and drain the vault.
 
Helpful endpoints:
- Faucet: `GET /faucet?to=0xYourAddress`
- Flag: `GET /flag` (only after solved)
 
Function selectors:
- deposit() -> 0xd0e30db0
- withdraw(uint256) -> 0x2e1a7d4d
- vault() -> 0xfbfa77cf
- isSolved() -> 0x64d98f6e
 
Flag format: `BITHAVEN{...}`