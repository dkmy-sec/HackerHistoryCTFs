// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/Setup.sol";

contract Deploy is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_KEY");
        uint256 vaultEth = vm.envUint("VAULT_WEI"); // in wei
            vm.startBroadcast(deployerKey);

            Setup setup = new Setup{value: vaultEth}();

            vm.stopBroadcast();

            console2.log("SETUP_ADDRESS", address(setup));
            console2.log("VAULT_ADDRESS", address(setup.vault()));
    }
}