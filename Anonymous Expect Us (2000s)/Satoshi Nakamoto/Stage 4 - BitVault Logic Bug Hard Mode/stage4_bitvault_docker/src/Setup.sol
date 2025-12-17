// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./BitVault.sol"

/**
 * Setup - deploys and seeds the vault.
 * Hard Mode: Server does NOT hand out the vault address directly.
 * Players must call vault() on Setup via raw calldata.
 */

contract Setup {
    BitVault public vault;

    constructor () payable {
        vault = new BitVault();
        // seed the vault with the setup funds
        (bool ok,) = address(vault).call{value: msg.value}("");
            require(ok, "seed failed");
    }

        function isSolved() external view returns (bool) {
            // solved when vault is drained below 0.01 ETH
            return address(vault).balance < 0.01 ether;
    }
}