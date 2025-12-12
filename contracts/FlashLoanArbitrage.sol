// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IPoolAddressesProvider} from "./interfaces/IPoolAddressesProvider.sol";
import {IPool} from "./interfaces/IPool.sol";
import {IERC20} from "./interfaces/IERC20.sol";
import {ISwapRouter} from "./interfaces/ISwapRouter.sol";

/**
 * @title FlashLoanArbitrage
 * @notice Contrato para executar arbitragem usando Flash Loans do Aave V3
 * @dev Implementa IFlashLoanSimpleReceiver para receber flash loans
 */
contract FlashLoanArbitrage {
    
    // ============================================================================
    // STATE VARIABLES
    // ============================================================================
    
    address public immutable owner;
    IPoolAddressesProvider public immutable ADDRESSES_PROVIDER;
    IPool public immutable POOL;
    
    // Routers das DEXs
    address public uniswapV3Router;
    address public pancakeSwapRouter;
    address public aerodromeRouter;
    
    // Controle de execução
    bool private locked;
    
    // Estatísticas
    uint256 public totalArbitrages;
    uint256 public totalProfit;
    
    // ============================================================================
    // EVENTS
    // ============================================================================
    
    event ArbitrageExecuted(
        address indexed token,
        uint256 amount,
        uint256 profit,
        address buyDex,
        address sellDex
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
    
    // ============================================================================
    // ERRORS
    // ============================================================================
    
    error Unauthorized();
    error ReentrancyGuard();
    error InsufficientProfit();
    error FlashLoanFailed();
    error TransferFailed();
    error InvalidParameters();
    
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
    
    // ============================================================================
    // CONSTRUCTOR
    // ============================================================================
    
    /**
     * @notice Inicializa o contrato com os endereços necessários
     * @param _addressProvider Endereço do Aave PoolAddressesProvider
     * @param _uniswapRouter Endereço do Uniswap V3 Router
     */
    constructor(
        address _addressProvider,
        address _uniswapRouter
    ) {
        owner = msg.sender;
        ADDRESSES_PROVIDER = IPoolAddressesProvider(_addressProvider);
        POOL = IPool(ADDRESSES_PROVIDER.getPool());
        uniswapV3Router = _uniswapRouter;
    }
    
    // ============================================================================
    // MAIN ARBITRAGE FUNCTION
    // ============================================================================
    
    /**
     * @notice Executa arbitragem usando flash loan
     * @param asset Endereço do token para flash loan
     * @param amount Quantidade para pegar emprestado
     * @param buyDex Endereço da DEX para comprar
     * @param sellDex Endereço da DEX para vender
     * @param tokenIn Token de entrada
     * @param tokenOut Token de saída
     * @param minProfit Lucro mínimo esperado
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        address buyDex,
        address sellDex,
        address tokenIn,
        address tokenOut,
        uint256 minProfit
    ) external onlyOwner nonReentrant {
        
        // Validações
        if (amount == 0 || minProfit == 0) revert InvalidParameters();
        
        // Preparar dados para o callback
        bytes memory params = abi.encode(
            buyDex,
            sellDex,
            tokenIn,
            tokenOut,
            minProfit
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
            uint256 minProfit
        ) = abi.decode(params, (address, address, address, address, uint256));
        
        // PASSO 1: Comprar na DEX mais barata
        uint256 amountOut = _swapOnDex(
            buyDex,
            tokenIn,
            tokenOut,
            amount
        );
        
        // PASSO 2: Vender na DEX mais cara
        uint256 finalAmount = _swapOnDex(
            sellDex,
            tokenOut,
            tokenIn,
            amountOut
        );
        
        // PASSO 3: Calcular lucro
        uint256 totalDebt = amount + premium;
        
        if (finalAmount <= totalDebt) revert InsufficientProfit();
        
        uint256 profit = finalAmount - totalDebt;
        
        if (profit < minProfit) revert InsufficientProfit();
        
        // PASSO 4: Aprovar pagamento do flash loan
        IERC20(asset).approve(address(POOL), totalDebt);
        
        // Atualizar estatísticas
        totalArbitrages++;
        totalProfit += profit;
        
        emit ArbitrageExecuted(
            asset,
            amount,
            profit,
            buyDex,
            sellDex
        );
        
        return true;
    }
    
    // ============================================================================
    // INTERNAL SWAP FUNCTIONS
    // ============================================================================
    
    /**
     * @notice Executa swap em uma DEX
     * @param dex Endereço do router da DEX
     * @param tokenIn Token de entrada
     * @param tokenOut Token de saída
     * @param amountIn Quantidade de entrada
     * @return amountOut Quantidade recebida
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
        } else if (keccak256(bytes(dexName)) == keccak256(bytes("pancake"))) {
            pancakeSwapRouter = routerAddress;
        } else if (keccak256(bytes(dexName)) == keccak256(bytes("aerodrome"))) {
            aerodromeRouter = routerAddress;
        }
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
        uint256 _totalProfit,
        address _owner
    ) {
        return (totalArbitrages, totalProfit, owner);
    }
    
    // Permitir receber ETH/BNB
    receive() external payable {}
}
