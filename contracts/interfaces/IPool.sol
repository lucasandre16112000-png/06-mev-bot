// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IPool
 * @notice Interface do Aave V3 Pool
 */
interface IPool {
    
    /**
     * @notice Executa flash loan simples
     * @param receiverAddress Endereço que receberá o callback
     * @param asset Endereço do token
     * @param amount Quantidade
     * @param params Dados extras
     * @param referralCode Código de referência
     */
    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external;
    
    /**
     * @notice Executa flash loan de múltiplos ativos
     */
    function flashLoan(
        address receiverAddress,
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata interestRateModes,
        address onBehalfOf,
        bytes calldata params,
        uint16 referralCode
    ) external;
}
