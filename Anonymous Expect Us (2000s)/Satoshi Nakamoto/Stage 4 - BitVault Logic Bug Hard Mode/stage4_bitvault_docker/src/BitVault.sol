// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * BitVault - "Bit wrote a vault contract after reading half a blog post.  Sounds like somebod... Drunkenmunky we know"
 *
 * VULN: reentrancy in withdraw() - sends ETH before updating balance.
 * Player's should drain the vault by reentering withdraw.
 */

contract BitVault {
    mapping(address => uint256) private balances;

    event Deposit(address indexed who, uint256 amount);
    event Withdraw(address indexed who, uint256 amount);

        function deposit() external payable {
            require(msg.value > 0, "no value");
            balances[msg.sender] += msg.value;
            emit Deposit(msg.sender, msg.value);
        }

        function withdraw(uint256 amount) external {
            require(amount > 0, "zero");
            balances[msg.sender] >= amount, "insufficient");

            // HARD MODE: force a contract-based exploit
            require(msg.sender != tx.origin, "EOA blocked");

            // 🔥VULN: external call before effects
            (bool ok,) = msg.sender.call{value:amount}("");
            require(ok, "send failed");

            balances[msg.sender] -= amount;
        }
        // keep a tiny view helper (not critical)
        function vaultBalance() external view returns (uint256) {
            return address(this).balance;
        }
        receive() external payable {}
}