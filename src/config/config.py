"""
⚙️ CONFIGURAÇÃO DO BOT - VERSÃO CORRIGIDA E OTIMIZADA
Todas as configurações centralizadas e validadas
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional
from dotenv import load_dotenv
from loguru import logger

# Carregar variáveis de ambiente
load_dotenv()

@dataclass
class NetworkConfig:
    """Configuração de uma rede blockchain"""
    name: str
    chain_id: int
    rpc_url: str
    native_token: str
    explorer_url: str
    priority: float  # 0.0 a 1.0
    enabled: bool = True


class BotConfig:
    """Configuração global do bot - VERSÃO CORRIGIDA"""
    
    # ============================================================================
    # MODO DE OPERAÇÃO
    # ============================================================================
    USE_TESTNET = os.getenv("USE_TESTNET", "true").lower() == "true"
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # ============================================================================
    # CREDENCIAIS
    # ============================================================================
    ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
    WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")
    
    # ============================================================================
    # CONVERSÃO DE PREÇOS (NOVO!)
    # ============================================================================
    ETH_PRICE_USD = float(os.getenv("ETH_PRICE_USD", "3500"))
    BNB_PRICE_USD = float(os.getenv("BNB_PRICE_USD", "600"))
    ARB_PRICE_USD = float(os.getenv("ARB_PRICE_USD", "1.2"))
    
    # ============================================================================
    # PARÂMETROS DE ARBITRAGEM
    # ============================================================================
    MIN_PROFIT_USD = float(os.getenv("MIN_PROFIT_USD", "5"))
    MIN_PROFIT_PERCENTAGE = float(os.getenv("MIN_PROFIT_PERCENTAGE", "0.5"))
    MAX_SLIPPAGE = float(os.getenv("MAX_SLIPPAGE", "1.0"))
    
    # ============================================================================
    # GESTÃO DE RISCO (CORRIGIDO!)
    # ============================================================================
    MAX_DAILY_GAS_SPEND = float(os.getenv("MAX_DAILY_GAS_SPEND", "10"))
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "20"))
    MAX_CONSECUTIVE_FAILURES = int(os.getenv("MAX_CONSECUTIVE_FAILURES", "5"))
    
    # ⚠️ CORRIGIDO: Agora em ETH/BNB, não USD!
    EMERGENCY_STOP_BALANCE = float(os.getenv("EMERGENCY_STOP_BALANCE", "0.001"))
    
    REINVEST_PERCENTAGE = float(os.getenv("REINVEST_PERCENTAGE", "0.5"))
    SIMULATE_BEFORE_EXECUTE = os.getenv("SIMULATE_BEFORE_EXECUTE", "true").lower() == "true"
    
    # ============================================================================
    # INTELIGÊNCIA ARTIFICIAL
    # ============================================================================
    ML_CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.60"))
    ML_TRAINING_INTERVAL = int(os.getenv("ML_TRAINING_INTERVAL", "100"))
    ML_MIN_TRAINING_SAMPLES = int(os.getenv("ML_MIN_TRAINING_SAMPLES", "50"))
    
    # ============================================================================
    # OPERAÇÃO
    # ============================================================================
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "5"))
    PRICE_UPDATE_INTERVAL = int(os.getenv("PRICE_UPDATE_INTERVAL", "10"))
    RUN_24_7 = os.getenv("RUN_24_7", "true").lower() == "true"
    
    # ============================================================================
    # FLASH LOAN
    # ============================================================================
    FLASH_LOAN_FEE = float(os.getenv("FLASH_LOAN_FEE", "0.0009"))  # 0.09%
    USE_FLASH_LOAN = os.getenv("USE_FLASH_LOAN", "true").lower() == "true"
    MAX_TRADE_AMOUNT_USD = float(os.getenv("MAX_TRADE_AMOUNT_USD", "1000"))
    
    # ============================================================================
    # SEGURANÇA
    # ============================================================================
    ENABLE_TOKEN_VERIFICATION = os.getenv("ENABLE_TOKEN_VERIFICATION", "true").lower() == "true"
    MIN_TOKEN_SECURITY_SCORE = int(os.getenv("MIN_TOKEN_SECURITY_SCORE", "70"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
    MAX_RECONNECTION_ATTEMPTS = int(os.getenv("MAX_RECONNECTION_ATTEMPTS", "3"))
    
    # ============================================================================
    # OTIMIZAÇÕES
    # ============================================================================
    PRICE_CACHE_DURATION = int(os.getenv("PRICE_CACHE_DURATION", "5"))
    TOKEN_VERIFICATION_CACHE = int(os.getenv("TOKEN_VERIFICATION_CACHE", "3600"))
    SCANNING_THREADS = int(os.getenv("SCANNING_THREADS", "3"))
    
    # ============================================================================
    # PATHS
    # ============================================================================
    DATA_DIR = os.getenv("DATA_DIR", "data")
    LOG_DIR = os.getenv("LOG_DIR", "data/logs")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    SAVE_ALL_OPPORTUNITIES = os.getenv("SAVE_ALL_OPPORTUNITIES", "true").lower() == "true"
    
    # ============================================================================
    # DASHBOARD
    # ============================================================================
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "3000"))
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    
    # ============================================================================
    # ALERTAS
    # ============================================================================
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    ENABLE_TELEGRAM_ALERTS = os.getenv("ENABLE_TELEGRAM_ALERTS", "false").lower() == "true"
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
    
    # ============================================================================
    # CONTROLE DE REDES
    # ============================================================================
    ENABLE_BASE = os.getenv("ENABLE_BASE", "true").lower() == "true"
    ENABLE_ARBITRUM = os.getenv("ENABLE_ARBITRUM", "true").lower() == "true"
    ENABLE_BSC = os.getenv("ENABLE_BSC", "true").lower() == "true"
    
    BASE_PRIORITY = float(os.getenv("BASE_PRIORITY", "50")) / 100
    ARBITRUM_PRIORITY = float(os.getenv("ARBITRUM_PRIORITY", "30")) / 100
    BSC_PRIORITY = float(os.getenv("BSC_PRIORITY", "20")) / 100


# ============================================================================
# CONFIGURAÇÕES DE REDES - CORRIGIDAS
# ============================================================================

# TESTNET - URLs CORRIGIDAS
NETWORKS_TESTNET = {}

if BotConfig.ENABLE_BASE:
    NETWORKS_TESTNET["base_sepolia"] = NetworkConfig(
        name="Base Sepolia",
        chain_id=84532,
        rpc_url=os.getenv("BASE_RPC_URL", f"https://base-sepolia.g.alchemy.com/v2/{BotConfig.ALCHEMY_API_KEY}"),
        native_token="ETH",
        explorer_url="https://sepolia.basescan.org",
        priority=BotConfig.BASE_PRIORITY,
        enabled=True
    )

if BotConfig.ENABLE_ARBITRUM:
    NETWORKS_TESTNET["arbitrum_sepolia"] = NetworkConfig(
        name="Arbitrum Sepolia",
        chain_id=421614,
        rpc_url=os.getenv("ARBITRUM_RPC_URL", f"https://arb-sepolia.g.alchemy.com/v2/{BotConfig.ALCHEMY_API_KEY}"),
        native_token="ETH",
        explorer_url="https://sepolia.arbiscan.io",
        priority=BotConfig.ARBITRUM_PRIORITY,
        enabled=True
    )

# ✅ ETHEREUM SEPOLIA (substitui BSC Testnet - Aave V3 não existe em BSC Testnet)
if BotConfig.ENABLE_BSC:
    NETWORKS_TESTNET["sepolia"] = NetworkConfig(
        name="Ethereum Sepolia",
        chain_id=11155111,
        rpc_url=os.getenv("SEPOLIA_RPC_URL", f"https://eth-sepolia.g.alchemy.com/v2/{BotConfig.ALCHEMY_API_KEY}"),
        native_token="ETH",
        explorer_url="https://sepolia.etherscan.io",
        priority=BotConfig.BSC_PRIORITY,
        enabled=True
    )

# MAINNET
NETWORKS_MAINNET = {}

if BotConfig.ENABLE_BASE:
    NETWORKS_MAINNET["base"] = NetworkConfig(
        name="Base",
        chain_id=8453,
        rpc_url=os.getenv("BASE_RPC_URL", f"https://base-mainnet.g.alchemy.com/v2/{BotConfig.ALCHEMY_API_KEY}"),
        native_token="ETH",
        explorer_url="https://basescan.org",
        priority=BotConfig.BASE_PRIORITY,
        enabled=True
    )

if BotConfig.ENABLE_ARBITRUM:
    NETWORKS_MAINNET["arbitrum"] = NetworkConfig(
        name="Arbitrum One",
        chain_id=42161,
        rpc_url=os.getenv("ARBITRUM_RPC_URL", f"https://arb-mainnet.g.alchemy.com/v2/{BotConfig.ALCHEMY_API_KEY}"),
        native_token="ETH",
        explorer_url="https://arbiscan.io",
        priority=BotConfig.ARBITRUM_PRIORITY,
        enabled=True
    )

if BotConfig.ENABLE_BSC:
    NETWORKS_MAINNET["bsc"] = NetworkConfig(
        name="BSC",
        chain_id=56,
        rpc_url=os.getenv("BSC_RPC_URL", "https://bsc-dataseed1.bnbchain.org"),
        native_token="BNB",
        explorer_url="https://bscscan.com",
        priority=BotConfig.BSC_PRIORITY,
        enabled=True
    )

# ============================================================================
# ENDEREÇOS DE CONTRATOS - COMPLETOS E CORRETOS
# ============================================================================

# Aave V3 Pool Addresses Provider
AAVE_V3_POOL = {
    # Mainnet
    "base": "0xe20fCBdBfFC4Dd138cE8b2E6FBb6CB49777ad64D",
    "arbitrum": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
    "bsc": "0x0000000000000000000000000000000000000000",  # Não disponível
    
    # Testnet - ✅ ENDEREÇOS CORRETOS DO REPOSITÓRIO OFICIAL AAVE
    "base_sepolia": "0x8bAB6d1b75f19e9eD9fCe8b9BD338844fF79aE27",  # ✅ Aave V3 Pool
    "arbitrum_sepolia": "0xBfC91D59fdAA134A4ED45f7B584cAf96D7792Eff",  # ✅ Aave V3 Pool
    "sepolia": "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951",  # ✅ Ethereum Sepolia (substitui BSC)
}

# Uniswap V3 Router
UNISWAP_V3_ROUTER = {
    # Mainnet
    "base": "0x2626664c2603336E57B271c5C0b26F421741e481",
    "arbitrum": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    "bsc": "0x0000000000000000000000000000000000000000",  # Não tem Uniswap V3
    
    # Testnet
    "base_sepolia": "0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4",
    "arbitrum_sepolia": "0x101F443B4d1b059569D643917553c771E1b9663E",
    "bsc_testnet": "0x0000000000000000000000000000000000000000",
}

# PancakeSwap V3 Router
PANCAKESWAP_V3_ROUTER = {
    # Mainnet
    "base": "0x678Aa4bF4E210cf2166753e054d5b7c31cc7fa86",
    "arbitrum": "0x1b81D678ffb9C0263b24A97847620C99d213eB14",
    "bsc": "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4",
    
    # Testnet
    "base_sepolia": "0x0000000000000000000000000000000000000000",
    "arbitrum_sepolia": "0x0000000000000000000000000000000000000000",
    "bsc_testnet": "0x9a489505a00cE272eAa5e07Dba6491314CaE3796",
}

# Aerodrome Router (Base only)
AERODROME_ROUTER = {
    "base": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43",
    "base_sepolia": "0x0000000000000000000000000000000000000000",
}

# Camelot Router (Arbitrum only)
CAMELOT_ROUTER = {
    "arbitrum": "0xc873fEcbd354f5A56E00E710B90EF4201db2448d",
    "arbitrum_sepolia": "0x0000000000000000000000000000000000000000",
}

# Tokens principais por rede
TOKENS = {
    "base": {
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "WETH": "0x4200000000000000000000000000000000000006",
        "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    },
    "base_sepolia": {
        "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # Testnet
        "WETH": "0x4200000000000000000000000000000000000006",
    },
    "arbitrum": {
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
        "DAI": "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
    },
    "arbitrum_sepolia": {
        "WETH": "0x980B62Da83eFf3D4576C647993b0c1D7faf17c73",
        "USDC": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d",
    },
    "bsc": {
        "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
        "DAI": "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",
    },
    "bsc_testnet": {
        "WBNB": "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd",
        "USDC": "0x64544969ed7EBf5f083679233325356EbE738930",
        "BUSD": "0xeD24FC36d5Ee211Ea25A80239Fb8C4Cfd80f12Ee",
    },
}


# ============================================================================
# FUNÇÕES AUXILIARES - NOVAS
# ============================================================================

def get_native_token_price(network: str) -> float:
    """Retorna preço do token nativo em USD"""
    if "bsc" in network:
        return BotConfig.BNB_PRICE_USD
    else:  # Base e Arbitrum usam ETH
        return BotConfig.ETH_PRICE_USD


def convert_native_to_usd(amount: float, network: str) -> float:
    """Converte quantidade de token nativo para USD"""
    price = get_native_token_price(network)
    return amount * price


def convert_usd_to_native(amount_usd: float, network: str) -> float:
    """Converte USD para quantidade de token nativo"""
    price = get_native_token_price(network)
    return amount_usd / price if price > 0 else 0


def validate_config() -> bool:
    """Valida configuração"""
    errors = []
    
    if not BotConfig.ALCHEMY_API_KEY:
        errors.append("ALCHEMY_API_KEY não configurada")
    
    if not BotConfig.PRIVATE_KEY:
        errors.append("PRIVATE_KEY não configurada")
    
    if not BotConfig.WALLET_ADDRESS:
        errors.append("WALLET_ADDRESS não configurado")
    
    if BotConfig.MIN_PROFIT_USD <= 0:
        errors.append("MIN_PROFIT_USD deve ser maior que 0")
    
    if BotConfig.EMERGENCY_STOP_BALANCE <= 0:
        errors.append("EMERGENCY_STOP_BALANCE deve ser maior que 0")
    
    if errors:
        for error in errors:
            logger.error(f"❌ {error}")
        return False
    
    logger.success("✅ Configuração validada!")
    return True


def print_config_summary():
    """Imprime resumo da configuração"""
    mode = "TESTNET" if BotConfig.USE_TESTNET else "MAINNET"
    networks = NETWORKS_TESTNET if BotConfig.USE_TESTNET else NETWORKS_MAINNET
    
    print("\n" + "="*60)
    print(f"🤖 BOT MEV - CONFIGURAÇÃO ({mode})")
    print("="*60)
    
    print(f"\n📡 Redes:")
    for net_name, net_config in networks.items():
        if net_config.enabled:
            print(f"  • {net_config.name} - Prioridade: {net_config.priority*100:.0f}%")
    
    print(f"\n💰 Arbitragem:")
    print(f"  • Lucro mínimo: ${BotConfig.MIN_PROFIT_USD}")
    print(f"  • Diferença mínima: {BotConfig.MIN_PROFIT_PERCENTAGE}%")
    
    print(f"\n🧠 IA: Confiança mínima {BotConfig.ML_CONFIDENCE_THRESHOLD*100:.0f}%")
    print(f"⛽ Gas: Máximo ${BotConfig.MAX_DAILY_GAS_SPEND}/dia")
    print(f"🛑 Stop: Saldo < {BotConfig.EMERGENCY_STOP_BALANCE} {networks[list(networks.keys())[0]].native_token}")
    print(f"⏰ Operação: {'24/7' if BotConfig.RUN_24_7 else 'Horário específico'}")
    
    if BotConfig.DRY_RUN:
        print(f"\n🎭 MODO DRY RUN: Transações serão SIMULADAS")
    else:
        print(f"\n💰 MODO REAL: Transações serão EXECUTADAS")
    
    print("\n" + "="*60 + "\n")

# ============================================================================
# MAJOR TOKENS - Lista de tokens principais para arbitragem
# ============================================================================

MAJOR_TOKENS = TOKENS  # Alias para compatibilidade
