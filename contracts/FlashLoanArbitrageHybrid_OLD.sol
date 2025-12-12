// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IPoolAddressesProvider} from "./interfaces/IPoolAddressesProvider.sol";
import {IPool} from "./interfaces/IPool.sol";
import {IERC20} from "./interfaces/IERC20.sol";
import {ISwapRouter} from "./interfaces/ISwapRouter.sol";

/**
 * @title FlashLoanArbitrageHybrid
 * @notice Contrato HÍBRIDO para executar arbitragem usando Flash Loans do Aave V3
 * @dev Funciona COM ou SEM Uniswap/PancakeSwap (adaptável por rede)
 * 
 * COMPATIBILIDADE:
 * - Base Sepolia: Aave V3 + Uniswap V3 ✅
 * - Arbitrum Sepolia: Aave V3 + Uniswap V3 ✅
 * - Ethereum Sepolia: SOMENTE Aave V3 (sem DEX externa) ✅
 */
contract FlashLoanArbitrageHybrid {
    
    // ============================================================================
    // STATE VARIABLES
    // ============================================================================
    
    address public immutable owner;
    IPoolAddressesProvider public immutable ADDRESSES_PROVIDER;
    IPool public immutable POOL;
    
    // Routers das DEXs (podem ser zero address se não disponíveis)
    address public uniswapV3Router;
    address public pancakeSwapRouter;
    address public aerodromeRouter;
    
    // Modo de operação
    bool public useExternalDEX; // true = usa Uniswap/Pancake, false = somente Aave
    
    // Controle de execução
    bool private locked;
    bool public paused;
    
    // Estatísticas
    uint256 public totalArbitrages;
    uint256 public successfulArbitrages;
    uint256 public failedArbitrages;
    uint256 public totalProfit;
    uint256 public totalGasSpent;
    uint256 public lastExecutionTime;
    
    // Tokens confiáveis (whitelist)
    mapping(address => bool) public trustedTokens;
    
    // ============================================================================
    // EVENTS
    // ============================================================================
    
    event ArbitrageExecuted(
        address indexed token,
        uint256 amount,
        uint256 profit,
        address buyDex,
        address sellDex,
        bool success
    );
    
    event FlashLoanReceived(
        address indexed asset,
        uint256 amount,
        uint256 premium
    );
    
    event ProfitWithdrawn(
        address indexed token,
        uint256 amount,
        address indexed to
    );
    
    event ModeChanged(bool useExternalDEX);
    
    // ============================================================================
    // ERRORS
    // ============================================================================
    
    error Unauthorized();
    error ReentrancyGuard();
    error InsufficientProfit();
    error FlashLoanFailed();
    error TransferFailed();
    error InvalidParameters();
    error ContractPaused();
    error UntrustedToken();
    
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
    
    // ============================================================================
    // CONSTRUCTOR
    // ============================================================================
    
    /**
     * @notice Inicializa o contrato HÍBRIDO
     * @param _addressProvider Endereço do Aave PoolAddressesProvider
     * @param _uniswapRouter Endereço do Uniswap V3 Router (ou address(0) se não disponível)
     */
    constructor(
        address _addressProvider,
        address _uniswapRouter
    ) {
        owner = msg.sender;
        ADDRESSES_PROVIDER = IPoolAddressesProvider(_addressProvider);
        POOL = IPool(ADDRESSES_PROVIDER.getPool());
        uniswapV3Router = _uniswapRouter;
        
        // Detectar automaticamente se deve usar DEX externa
        useExternalDEX = (_uniswapRouter != address(0));
        
        emit ModeChanged(useExternalDEX);
    }
    
    // ============================================================================
    // MAIN ARBITRAGE FUNCTION
    // ============================================================================
    
    /**
     * @notice Executa arbitragem usando flash loan
     * @param asset Endereço do token para flash loan
     * @param amount Quantidade para pegar emprestado
     * @param buyDex Endereço da DEX para comprar (ou address(0) para modo Aave-only)
     * @param sellDex Endereço da DEX para vender (ou address(0) para modo Aave-only)
     * @param tokenIn Token de entrada
     * @param tokenOut Token de saída
     * @param minProfit Lucro mínimo esperado
     * @param deadline Prazo para execução
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
    ) external onlyOwner nonReentrant whenNotPaused {
        
        // Validações
        if (amount == 0 || minProfit == 0) revert InvalidParameters();
        if (block.timestamp > deadline) revert InvalidParameters();
        
        // Verificar tokens confiáveis (se configurado)
        if (trustedTokens[address(0)] == false) { // Se whitelist está ativa
            if (!trustedTokens[tokenIn] || !trustedTokens[tokenOut]) {
                revert UntrustedToken();
            }
        }
        
        // Preparar dados para o callback
        bytes memory params = abi.encode(
            buyDex,
            sellDex,
            tokenIn,
            tokenOut,
            minProfit,
            deadline
        );
        
        // Solicitar flash loan
        POOL.flashLoanSimple(
            address(this),
            asset,
            amount,
            params,
            0 // referral code
        );
    }
    
    // ============================================================================
    // AAVE FLASH LOAN CALLBACK
    // ============================================================================
    
    /**
     * @notice Callback executado pelo Aave após receber o flash loan
     * @param asset Endereço do token emprestado
     * @param amount Quantidade emprestada
     * @param premium Taxa do flash loan
     * @param initiator Quem iniciou o flash loan
     * @param params Dados codificados
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        
        // Apenas o Pool pode chamar esta função
        if (msg.sender != address(POOL)) revert Unauthorized();
        if (initiator != address(this)) revert Unauthorized();
        
        emit FlashLoanReceived(asset, amount, premium);
        
        // Decodificar parâmetros
        (
            address buyDex,
            address sellDex,
            address tokenIn,
            address tokenOut,
            uint256 minProfit,
            uint256 deadline
        ) = abi.decode(params, (address, address, address, address, uint256, uint256));
        
        uint256 finalAmount;
        bool success = false;
        
        // Escolher estratégia baseado no modo
        if (useExternalDEX && buyDex != address(0) && sellDex != address(0)) {
            // MODO HÍBRIDO: Usar DEXs externas
            finalAmount = _executeWithExternalDEX(
                buyDex,
                sellDex,
                tokenIn,
                tokenOut,
                amount
            );
            success = true;
        } else {
            // MODO AAVE-ONLY: Usar somente Aave (para Ethereum Sepolia)
            // Neste modo, apenas testamos a capacidade de flash loan
            // Em produção, aqui você implementaria outra estratégia
            // (ex: arbitragem entre pools do próprio Aave)
            finalAmount = amount; // Simples: devolver o mesmo valor
            success = true;
        }
        
        // Calcular lucro
        uint256 totalDebt = amount + premium;
        
        if (finalAmount <= totalDebt) {
            failedArbitrages++;
            emit ArbitrageExecuted(asset, amount, 0, buyDex, sellDex, false);
            // Ainda assim, pagar o flash loan para não reverter
            IERC20(asset).approve(address(POOL), totalDebt);
            return true;
        }
        
        uint256 profit = finalAmount - totalDebt;
        
        if (profit < minProfit) {
            failedArbitrages++;
            emit ArbitrageExecuted(asset, amount, profit, buyDex, sellDex, false);
        } else {
            successfulArbitrages++;
            totalProfit += profit;
            emit ArbitrageExecuted(asset, amount, profit, buyDex, sellDex, true);
        }
        
        // Aprovar pagamento do flash loan
        IERC20(asset).approve(address(POOL), totalDebt);
        
        // Atualizar estatísticas
        totalArbitrages++;
        lastExecutionTime = block.timestamp;
        
        return true;
    }
    
    // ============================================================================
    // INTERNAL FUNCTIONS
    // ============================================================================
    
    /**
     * @notice Executa arbitragem usando DEXs externas
     */
    function _executeWithExternalDEX(
        address buyDex,
        address sellDex,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 finalAmount) {
        
        // PASSO 1: Comprar na DEX mais barata
        uint256 amountOut = _swapOnDex(
            buyDex,
            tokenIn,
            tokenOut,
            amountIn
        );
        
        // PASSO 2: Vender na DEX mais cara
        finalAmount = _swapOnDex(
            sellDex,
            tokenOut,
            tokenIn,
            amountOut
        );
        
        return finalAmount;
    }
    
    /**
     * @notice Executa swap em uma DEX
     */
    function _swapOnDex(
        address dex,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        
        // Aprovar DEX para gastar tokens
        IERC20(tokenIn).approve(dex, amountIn);
        
        // Verificar se é Uniswap V3 ou V2-like
        if (dex == uniswapV3Router) {
            amountOut = _swapUniswapV3(tokenIn, tokenOut, amountIn);
        } else {
            amountOut = _swapV2Like(dex, tokenIn, tokenOut, amountIn);
        }
        
        return amountOut;
    }
    
    /**
     * @notice Swap no Uniswap V3
     */
    function _swapUniswapV3(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter
            .ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: 3000, // 0.3%
                recipient: address(this),
                deadline: block.timestamp,
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });
        
        amountOut = ISwapRouter(uniswapV3Router).exactInputSingle(params);
    }
    
    /**
     * @notice Swap em DEXs V2-like (PancakeSwap, Aerodrome, etc)
     */
    function _swapV2Like(
        address router,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal returns (uint256 amountOut) {
        
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        // Interface simplificada de router V2
        (bool success, bytes memory data) = router.call(
            abi.encodeWithSignature(
                "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
                amountIn,
                0, // amountOutMin
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
    // ADMIN FUNCTIONS
    // ============================================================================
    
    /**
     * @notice Atualiza endereço de router
     */
    function setRouter(
        string calldata dexName,
        address routerAddress
    ) external onlyOwner {
        if (keccak256(bytes(dexName)) == keccak256(bytes("uniswap"))) {
            uniswapV3Router = routerAddress;
            useExternalDEX = (routerAddress != address(0));
        } else if (keccak256(bytes(dexName)) == keccak256(bytes("pancake"))) {
            pancakeSwapRouter = routerAddress;
        } else if (keccak256(bytes(dexName)) == keccak256(bytes("aerodrome"))) {
            aerodromeRouter = routerAddress;
        }
        
        emit ModeChanged(useExternalDEX);
    }
    
    /**
     * @notice Define token como confiável
     */
    function setTrustedToken(address token, bool status) external onlyOwner {
        trustedTokens[token] = status;
    }
    
    /**
     * @notice Pausa/despausa contrato
     */
    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
    }
    
    /**
     * @notice Saca lucros acumulados
     */
    function withdrawProfit(
        address token,
        uint256 amount
    ) external onlyOwner {
        
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amount > balance) amount = balance;
        
        bool success = IERC20(token).transfer(owner, amount);
        if (!success) revert TransferFailed();
        
        emit ProfitWithdrawn(token, amount, owner);
    }
    
    /**
     * @notice Saca todo o saldo de um token
     */
    function withdrawAll(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        if (balance > 0) {
            bool success = IERC20(token).transfer(owner, balance);
            if (!success) revert TransferFailed();
            emit ProfitWithdrawn(token, balance, owner);
        }
    }
    
    /**
     * @notice Função de emergência para recuperar ETH/BNB
     */
    function withdrawNative() external onlyOwner {
        (bool success, ) = owner.call{value: address(this).balance}("");
        if (!success) revert TransferFailed();
    }
    
    // ============================================================================
    // VIEW FUNCTIONS
    // ============================================================================
    
    /**
     * @notice Retorna saldo de um token no contrato
     */
    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
    
    /**
     * @notice Retorna estatísticas do contrato
     */
    function getStats() external view returns (
        uint256 _totalArbitrages,
        uint256 _successfulArbitrages,
        uint256 _failedArbitrages,
        uint256 _totalProfit,
        uint256 _totalGasSpent,
        uint256 _averageProfit,
        uint256 _lastExecutionTime
    ) {
        uint256 avgProfit = totalArbitrages > 0 ? totalProfit / totalArbitrages : 0;
        return (
            totalArbitrages,
            successfulArbitrages,
            failedArbitrages,
            totalProfit,
            totalGasSpent,
            avgProfit,
            lastExecutionTime
        );
    }
    
    /**
     * @notice Retorna modo de operação
     */
    function getMode() external view returns (string memory) {
        if (useExternalDEX) {
            return "HYBRID: Aave + External DEX";
        } else {
            return "AAVE-ONLY: Flash Loan Only";
        }
    }
    
    // Permitir receber ETH/BNB
    receive() external payable {}
}
