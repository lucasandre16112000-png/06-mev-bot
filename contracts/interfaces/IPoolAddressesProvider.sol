// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IPoolAddressesProvider
 * @notice Interface do Aave PoolAddressesProvider
 */
interface IPoolAddressesProvider {
    function getPool() external view returns (address);
    function getPriceOracle() external view returns (address);
}
