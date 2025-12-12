// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IPool} from "./interfaces/IPool.sol";
import {IERC20} from "./interfaces/IERC20.sol";
import {ISwapRouter} from "./interfaces/ISwapRouter.sol";

/**
 * @title FlashLoanArbitrageHybrid
 * @notice Contrato híbrido para arbitragem MEV com Flash Loans
 * @dev Versão OTIMIZADA - Sem erro "Stack too deep"
 * 
 * MODOS DE OPERAÇÃO:
 * - HYBRID: Usa Aave V3 + DEXs externas (Uniswap/PancakeSwap)
 * - AAVE-ONLY: Usa apenas Aave V3 (para redes sem Uniswap como Ethereum Sepolia)
 */
contract FlashLoanArbitrageHybrid {
    
    // ============================================================
    // ERROS CUSTOMIZADOS
    // ============================================================
    
    error Unauthorized();
    error InvalidAmount();
    error InsufficientProfit();
    error SwapFailed();
    
    // ============================================================
    // VARIÁVEIS DE ESTADO
    // ============================================================
    
    IPool public immutable POOL;
    address public immutable owner;
    bool public useExternalDEX;
    
    // Estatísticas
    uint256 public totalArbitrages;
    uint256 public successfulArbitrages;
    uint256 public failedArbitrages;
    uint256 public totalProfit;
    uint256 public lastExecutionTime;
    
    // ============================================================
    // EVENTOS
    // ============================================================
    
    event FlashLoanReceived(address indexed asset, uint256 amount, uint256 premium);
    event ArbitrageExecuted(
        address indexed asset,
        uint256 amount,
        uint256 profit,
        address buyDex,
        address sellDex,
        bool success
    );
    event ModeChanged(bool useExternalDEX);
    event FundsWithdrawn(address indexed token, uint256 amount);
    
    // ============================================================
    // STRUCTS (para reduzir variáveis locais)
    // ============================================================
    
    struct ArbitrageParams {
        address buyDex;
        address sellDex;
        address tokenIn;
        address tokenOut;
        uint256 minProfit;
        uint256 deadline;
    }
    
    struct ExecutionResult {
        uint256 finalAmount;
        uint256 totalDebt;
        uint256 profit;
        bool success;
    }
    
    // ============================================================
    // MODIFICADORES
    // ============================================================
    
    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }
    
    // ============================================================
    // CONSTRUTOR
    // ============================================================
    
    /**
     * @param poolAddress Endereço do Aave V3 Pool
     * @param _useExternalDEX Se true, usa DEXs externas (modo HYBRID)
     */
    constructor(address poolAddress, bool _useExternalDEX) {
        POOL = IPool(poolAddress);
        owner = msg.sender;
        useExternalDEX = _useExternalDEX;
    }
    
    // ============================================================
    // FUNÇÕES PRINCIPAIS
    // ============================================================
    
    /**
     * @notice Executa arbitragem com flash loan
     * @param asset Token para emprestar
     * @param amount Quantidade para emprestar
     * @param params Parâmetros codificados da arbitragem
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) external onlyOwner {
        if (amount == 0) revert InvalidAmount();
        
        address[] memory assets = new address[](1);
        assets[0] = asset;
        
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amount;
        
        uint256[] memory modes = new uint256[](1);
        modes[0] = 0; // 0 = sem dívida, pagar na mesma transação
        
        POOL.flashLoan(
            address(this),
            assets,
            amounts,
            modes,
            address(this),
            params,
            0
        );
    }
    
    /**
     * @notice Callback do Aave após receber flash loan
     * @dev OTIMIZADO - Usa structs para reduzir variáveis locais
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        
        // Validações
        if (msg.sender != address(POOL)) revert Unauthorized();
        if (initiator != address(this)) revert Unauthorized();
        
        emit FlashLoanReceived(asset, amount, premium);
        
        // Decodificar parâmetros em struct
        ArbitrageParams memory arbParams = abi.decode(params, (ArbitrageParams));
        
        // Executar arbitragem
        ExecutionResult memory result = _executeArbitrageLogic(
            asset,
            amount,
            premium,
            arbParams
        );
        
        // Aprovar pagamento do flash loan
        IERC20(asset).approve(address(POOL), result.totalDebt);
        
        // Atualizar estatísticas
        _updateStats(result.success);
        
        // Emitir evento
        emit ArbitrageExecuted(
            asset,
            amount,
            result.profit,
            arbParams.buyDex,
            arbParams.sellDex,
            result.success
        );
        
        return true;
    }
    
    // ============================================================
    // FUNÇÕES INTERNAS (OTIMIZADAS)
    // ============================================================
    
    /**
     * @dev Lógica principal de arbitragem (refatorada)
     */
    function _executeArbitrageLogic(
        address asset,
        uint256 amount,
        uint256 premium,
        ArbitrageParams memory params
    ) internal returns (ExecutionResult memory) {
        
        ExecutionResult memory result;
        result.totalDebt = amount + premium;
        
        // Escolher estratégia baseado no modo
        if (useExternalDEX && params.buyDex != address(0) && params.sellDex != address(0)) {
            // MODO HÍBRIDO: Usar DEXs externas
            result.finalAmount = _executeWithExternalDEX(
                params.buyDex,
                params.sellDex,
                params.tokenIn,
                params.tokenOut,
                amount
            );
        } else {
            // MODO AAVE-ONLY: Simples retorno
            result.finalAmount = amount;
        }
        
        // Calcular lucro
        if (result.finalAmount > result.totalDebt) {
            result.profit = result.finalAmount - result.totalDebt;
            result.success = (result.profit >= params.minProfit);
        } else {
            result.profit = 0;
            result.success = false;
        }
        
        return result;
    }
    
    /**
     * @dev Executa arbitragem usando DEXs externas
     */
    function _executeWithExternalDEX(
        address buyDex,
        address sellDex,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256) {
        
        // 1. Aprovar buyDex
        IERC20(tokenIn).approve(buyDex, amountIn);
        
        // 2. Comprar tokenOut na buyDex
        ISwapRouter.ExactInputSingleParams memory buyParams = ISwapRouter.ExactInputSingleParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            fee: 3000,
            recipient: address(this),
            deadline: block.timestamp + 300,
            amountIn: amountIn,
            amountOutMinimum: 0,
            sqrtPriceLimitX96: 0
        });
        
        uint256 amountOut = ISwapRouter(buyDex).exactInputSingle(buyParams);
        
        // 3. Aprovar sellDex
        IERC20(tokenOut).approve(sellDex, amountOut);
        
        // 4. Vender tokenOut na sellDex
        ISwapRouter.ExactInputSingleParams memory sellParams = ISwapRouter.ExactInputSingleParams({
            tokenIn: tokenOut,
            tokenOut: tokenIn,
            fee: 3000,
            recipient: address(this),
            deadline: block.timestamp + 300,
            amountIn: amountOut,
            amountOutMinimum: 0,
            sqrtPriceLimitX96: 0
        });
        
        uint256 finalAmount = ISwapRouter(sellDex).exactInputSingle(sellParams);
        
        return finalAmount;
    }
    
    /**
     * @dev Atualiza estatísticas
     */
    function _updateStats(bool success) internal {
        totalArbitrages++;
        lastExecutionTime = block.timestamp;
        
        if (success) {
            successfulArbitrages++;
        } else {
            failedArbitrages++;
        }
    }
    
    // ============================================================
    // FUNÇÕES DE ADMINISTRAÇÃO
    // ============================================================
    
    /**
     * @notice Alterna modo de operação
     */
    function setUseExternalDEX(bool _useExternalDEX) external onlyOwner {
        useExternalDEX = _useExternalDEX;
        emit ModeChanged(_useExternalDEX);
    }
    
    /**
     * @notice Retira fundos do contrato
     */
    function withdraw(address token, uint256 amount) external onlyOwner {
        if (token == address(0)) {
            payable(owner).transfer(amount);
        } else {
            IERC20(token).transfer(owner, amount);
        }
        emit FundsWithdrawn(token, amount);
    }
    
    /**
     * @notice Retira todos os fundos de um token
     */
    function withdrawAll(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (balance > 0) {
            IERC20(token).transfer(owner, balance);
            emit FundsWithdrawn(token, balance);
        }
    }
    
    // ============================================================
    // FUNÇÕES DE VISUALIZAÇÃO
    // ============================================================
    
    /**
     * @notice Retorna modo de operação
     */
    function getMode() external view returns (string memory) {
        return useExternalDEX ? "HYBRID: Aave + External DEX" : "AAVE-ONLY: Flash Loan Only";
    }
    
    /**
     * @notice Retorna estatísticas
     */
    function getStats() external view returns (
        uint256 _totalArbitrages,
        uint256 _successfulArbitrages,
        uint256 _failedArbitrages,
        uint256 _totalProfit,
        uint256 _lastExecutionTime
    ) {
        return (
            totalArbitrages,
            successfulArbitrages,
            failedArbitrages,
            totalProfit,
            lastExecutionTime
        );
    }
    
    /**
     * @notice Retorna saldo de um token
     */
    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
    
    // ============================================================
    // FUNÇÃO RECEIVE
    // ============================================================
    
    receive() external payable {}
}
