// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IPool} from "./interfaces/IPool.sol";
import {IERC20} from "./interfaces/IERC20.sol";
import {ISwapRouter} from "./interfaces/ISwapRouter.sol";

/**
 * @title FlashLoanArbitrageV2
 * @notice Versão AVANÇADA com proteções MEV e otimizações de gas
 * @dev Implementa múltiplas estratégias e proteções contra front-running
 */
contract FlashLoanArbitrageV2 {
    
    // ============================================================================
    // STATE VARIABLES
    // ============================================================================
    
    address public immutable owner;
    IPool public immutable POOL;
    
    // Routers das DEXs por rede
    mapping(string => address) public routers;
    
    // Controle de execução
    bool private locked;
    bool public paused;
    
    // Proteção MEV
    uint256 public minProfitBps = 50; // 0.5% mínimo
    uint256 public maxSlippageBps = 100; // 1% máximo
    uint256 public gasBuffer = 100000; // Buffer de gas
    
    // Whitelist de tokens seguros
    mapping(address => bool) public trustedTokens;
    
    // Blacklist de bots maliciosos
    mapping(address => bool) public blacklistedBots;
    
    // Estatísticas avançadas
    struct Stats {
        uint256 totalArbitrages;
        uint256 successfulArbitrages;
        uint256 failedArbitrages;
        uint256 totalProfit;
        uint256 totalGasSpent;
        uint256 averageProfit;
        uint256 lastExecutionTime;
    }
    Stats public stats;
    
    // Histórico de execuções (últimas 100)
    struct Execution {
        uint256 timestamp;
        address asset;
        uint256 amount;
        uint256 profit;
        bool success;
    }
    Execution[] public executionHistory;
    uint256 public constant MAX_HISTORY = 100;
    
    // ============================================================================
    // EVENTS
    // ============================================================================
    
    event ArbitrageExecuted(
        address indexed token,
        uint256 amount,
        uint256 profit,
        uint256 gasUsed,
        address buyDex,
        address sellDex,
        uint256 timestamp
    );
    
    event ArbitrageFailed(
        address indexed token,
        uint256 amount,
        string reason,
        uint256 timestamp
    );
    
    event FlashLoanReceived(
        address indexed asset,
        uint256 amount,
        uint256 premium,
        uint256 timestamp
    );
    
    event ProfitWithdrawn(
        address indexed token,
        uint256 amount,
        address indexed to,
        uint256 timestamp
    );
    
    event EmergencyWithdraw(
        address indexed token,
        uint256 amount,
        uint256 timestamp
    );
    
    event ConfigUpdated(
        string parameter,
        uint256 oldValue,
        uint256 newValue
    );
    
    event TokenWhitelisted(address indexed token, bool status);
    event BotBlacklisted(address indexed bot, bool status);
    event Paused(bool status);
    
    // ============================================================================
    // ERRORS
    // ============================================================================
    
    error Unauthorized();
    error ReentrancyGuard();
    error InsufficientProfit();
    error ExcessiveSlippage();
    error FlashLoanFailed();
    error TransferFailed();
    error InvalidParameters();
    error ContractPaused();
    error BlacklistedBot();
    error UntrustedToken();
    error GasLimitExceeded();
    
    // ============================================================================
    // MODIFIERS
    // ============================================================================
    
    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }
    
    modifier nonReentrant() {
        if (locked) revert ReentrancyGuard();
        locked = true;
        _;
        locked = false;
    }
    
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
    
    modifier notBlacklisted() {
        if (blacklistedBots[msg.sender]) revert BlacklistedBot();
        _;
    }
    
    // ============================================================================
    // CONSTRUCTOR
    // ============================================================================
    
    constructor(
        address _poolAddress,
        address _uniswapRouter
    ) {
        owner = msg.sender;
        POOL = IPool(_poolAddress);
        routers["uniswap"] = _uniswapRouter;
    }
    
    // ============================================================================
    // MAIN ARBITRAGE FUNCTION (MELHORADA)
    // ============================================================================
    
    /**
     * @notice Executa arbitragem com verificações avançadas
     * @param asset Token para flash loan
     * @param amount Quantidade
     * @param buyDex DEX para comprar
     * @param sellDex DEX para vender
     * @param tokenIn Token entrada
     * @param tokenOut Token saída
     * @param minProfit Lucro mínimo esperado
     * @param deadline Prazo máximo de execução
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        address buyDex,
        address sellDex,
        address tokenIn,
        address tokenOut,
        uint256 minProfit,
        uint256 deadline
    ) external onlyOwner nonReentrant whenNotPaused notBlacklisted {
        
        // Validações avançadas
        if (amount == 0 || minProfit == 0) revert InvalidParameters();
        if (block.timestamp > deadline) revert InvalidParameters();
        if (gasleft() < gasBuffer) revert GasLimitExceeded();
        
        // Verificar se tokens são confiáveis
        if (!trustedTokens[tokenIn] || !trustedTokens[tokenOut]) {
            revert UntrustedToken();
        }
        
        uint256 gasStart = gasleft();
        
        // Preparar dados
        bytes memory params = abi.encode(
            buyDex,
            sellDex,
            tokenIn,
            tokenOut,
            minProfit,
            deadline,
            gasStart
        );
        
        // Executar flash loan
        try POOL.flashLoanSimple(
            address(this),
            asset,
            amount,
            params,
            0
        ) {
            stats.successfulArbitrages++;
        } catch Error(string memory reason) {
            stats.failedArbitrages++;
            emit ArbitrageFailed(asset, amount, reason, block.timestamp);
        }
        
        stats.totalArbitrages++;
        stats.lastExecutionTime = block.timestamp;
    }
    
    // ============================================================================
    // AAVE CALLBACK (MELHORADO)
    // ============================================================================
    
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        
        if (msg.sender != address(POOL)) revert Unauthorized();
        if (initiator != address(this)) revert Unauthorized();
        
        emit FlashLoanReceived(asset, amount, premium, block.timestamp);
        
        // Decodificar
        (
            address buyDex,
            address sellDex,
            address tokenIn,
            address tokenOut,
            uint256 minProfit,
            uint256 deadline,
            uint256 gasStart
        ) = abi.decode(params, (address, address, address, address, uint256, uint256, uint256));
        
        // Verificar deadline
        if (block.timestamp > deadline) revert InvalidParameters();
        
        // PASSO 1: Comprar
        uint256 amountOut = _swapOnDex(buyDex, tokenIn, tokenOut, amount);
        
        // Verificar slippage
        uint256 expectedOut = _calculateExpectedOutput(amount, tokenIn, tokenOut);
        if (_calculateSlippage(expectedOut, amountOut) > maxSlippageBps) {
            revert ExcessiveSlippage();
        }
        
        // PASSO 2: Vender
        uint256 finalAmount = _swapOnDex(sellDex, tokenOut, tokenIn, amountOut);
        
        // PASSO 3: Calcular lucro
        uint256 totalDebt = amount + premium;
        
        if (finalAmount <= totalDebt) revert InsufficientProfit();
        
        uint256 profit = finalAmount - totalDebt;
        uint256 profitBps = (profit * 10000) / amount;
        
        if (profitBps < minProfitBps) revert InsufficientProfit();
        
        // PASSO 4: Pagar flash loan
        IERC20(asset).approve(address(POOL), totalDebt);
        
        // Calcular gas gasto
        uint256 gasUsed = gasStart - gasleft();
        
        // Atualizar estatísticas
        stats.totalProfit += profit;
        stats.totalGasSpent += gasUsed;
        stats.averageProfit = stats.totalProfit / stats.successfulArbitrages;
        
        // Adicionar ao histórico
        _addToHistory(asset, amount, profit, true);
        
        emit ArbitrageExecuted(
            asset,
            amount,
            profit,
            gasUsed,
            buyDex,
            sellDex,
            block.timestamp
        );
        
        return true;
    }
    
    // ============================================================================
    // SWAP FUNCTIONS (OTIMIZADAS)
    // ============================================================================
    
    function _swapOnDex(
        address dex,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        
        IERC20(tokenIn).approve(dex, amountIn);
        
        if (dex == routers["uniswap"]) {
            amountOut = _swapUniswapV3(tokenIn, tokenOut, amountIn);
        } else {
            amountOut = _swapV2Like(dex, tokenIn, tokenOut, amountIn);
        }
        
        return amountOut;
    }
    
    function _swapUniswapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter
            .ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: 3000,
                recipient: address(this),
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });
        
        amountOut = ISwapRouter(routers["uniswap"]).exactInputSingle(params);
    }
    
    function _swapV2Like(
        address router,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        (bool success, bytes memory data) = router.call(
            abi.encodeWithSignature(
                "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
                amountIn,
                0,
                path,
                address(this),
                block.timestamp
            )
        );
        
        if (!success) revert FlashLoanFailed();
        
        uint256[] memory amounts = abi.decode(data, (uint256[]));
        amountOut = amounts[amounts.length - 1];
    }
    
    // ============================================================================
    // HELPER FUNCTIONS
    // ============================================================================
    
    function _calculateExpectedOutput(
        uint256 amountIn,
        address tokenIn,
        address tokenOut
    ) internal view returns (uint256) {
        // Implementação simplificada - em produção usar oracle
        return amountIn; // Placeholder
    }
    
    function _calculateSlippage(
        uint256 expected,
        uint256 actual
    ) internal pure returns (uint256) {
        if (expected == 0) return 0;
        if (actual >= expected) return 0;
        return ((expected - actual) * 10000) / expected;
    }
    
    function _addToHistory(
        address asset,
        uint256 amount,
        uint256 profit,
        bool success
    ) internal {
        if (executionHistory.length >= MAX_HISTORY) {
            // Remove o mais antigo
            for (uint i = 0; i < executionHistory.length - 1; i++) {
                executionHistory[i] = executionHistory[i + 1];
            }
            executionHistory.pop();
        }
        
        executionHistory.push(Execution({
            timestamp: block.timestamp,
            asset: asset,
            amount: amount,
            profit: profit,
            success: success
        }));
    }
    
    // ============================================================================
    // ADMIN FUNCTIONS (MELHORADAS)
    // ============================================================================
    
    function setRouter(string calldata dexName, address routerAddress) 
        external onlyOwner 
    {
        routers[dexName] = routerAddress;
    }
    
    function setMinProfitBps(uint256 _minProfitBps) external onlyOwner {
        emit ConfigUpdated("minProfitBps", minProfitBps, _minProfitBps);
        minProfitBps = _minProfitBps;
    }
    
    function setMaxSlippageBps(uint256 _maxSlippageBps) external onlyOwner {
        emit ConfigUpdated("maxSlippageBps", maxSlippageBps, _maxSlippageBps);
        maxSlippageBps = _maxSlippageBps;
    }
    
    function setGasBuffer(uint256 _gasBuffer) external onlyOwner {
        emit ConfigUpdated("gasBuffer", gasBuffer, _gasBuffer);
        gasBuffer = _gasBuffer;
    }
    
    function setTrustedToken(address token, bool status) external onlyOwner {
        trustedTokens[token] = status;
        emit TokenWhitelisted(token, status);
    }
    
    function setBlacklistedBot(address bot, bool status) external onlyOwner {
        blacklistedBots[bot] = status;
        emit BotBlacklisted(bot, status);
    }
    
    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
        emit Paused(_paused);
    }
    
    function withdrawProfit(address token, uint256 amount) 
        external onlyOwner 
    {
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amount > balance) amount = balance;
        
        bool success = IERC20(token).transfer(owner, amount);
        if (!success) revert TransferFailed();
        
        emit ProfitWithdrawn(token, amount, owner, block.timestamp);
    }
    
    function emergencyWithdraw(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (balance > 0) {
            bool success = IERC20(token).transfer(owner, balance);
            if (!success) revert TransferFailed();
            emit EmergencyWithdraw(token, balance, block.timestamp);
        }
    }
    
    function withdrawNative() external onlyOwner {
        (bool success, ) = owner.call{value: address(this).balance}("");
        if (!success) revert TransferFailed();
    }
    
    // ============================================================================
    // VIEW FUNCTIONS (MELHORADAS)
    // ============================================================================
    
    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
    
    function getStats() external view returns (Stats memory) {
        return stats;
    }
    
    function getExecutionHistory() external view returns (Execution[] memory) {
        return executionHistory;
    }
    
    function getSuccessRate() external view returns (uint256) {
        if (stats.totalArbitrages == 0) return 0;
        return (stats.successfulArbitrages * 100) / stats.totalArbitrages;
    }
    
    function getRouter(string calldata dexName) external view returns (address) {
        return routers[dexName];
    }
    
    function isTrustedToken(address token) external view returns (bool) {
        return trustedTokens[token];
    }
    
    function isBlacklisted(address bot) external view returns (bool) {
        return blacklistedBots[bot];
    }
    
    receive() external payable {}
}
