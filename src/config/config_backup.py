"""
🔧 CONFIGURAÇÕES PRINCIPAIS DO BOT MEV
Arquivo central de configuração para Base, Arbitrum e BSC
"""

import os
from typing import Dict
from dataclasses import dataclass
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ============================================================================
# CONFIGURAÇÕES DE REDE (MAINNET E TESTNET)
# ============================================================================

@dataclass
class NetworkConfig:
    """Configuração de uma blockchain"""
    name: str
    chain_id: int
    rpc_url: str
    explorer_url: str
    native_token: str
    priority_weight: float  # Peso de priorização (60%, 25%, 15%)
    gas_price_multiplier: float
    max_gas_price_gwei: float
    
# MAINNET CONFIGS
NETWORKS_MAINNET = {
    "base": NetworkConfig(
        name="Base",
        chain_id=8453,
        rpc_url=f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
        explorer_url="https://basescan.org",
        native_token="ETH",
        priority_weight=0.60,  # 60% de prioridade
        gas_price_multiplier=1.1,
        max_gas_price_gwei=50.0
    ),
    "arbitrum": NetworkConfig(
        name="Arbitrum",
        chain_id=42161,
        rpc_url=f"https://arb-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
        explorer_url="https://arbiscan.io",
        native_token="ETH",
        priority_weight=0.25,  # 25% de prioridade
        gas_price_multiplier=1.15,
        max_gas_price_gwei=100.0
    ),
    "bsc": NetworkConfig(
        name="BSC",
        chain_id=56,
        rpc_url="https://bsc-dataseed1.binance.org",  # BSC não precisa Alchemy
        explorer_url="https://bscscan.com",
        native_token="BNB",
        priority_weight=0.15,  # 15% de prioridade
        gas_price_multiplier=1.2,
        max_gas_price_gwei=10.0
    )
}

# TESTNET CONFIGS
NETWORKS_TESTNET = {
    "base_sepolia": NetworkConfig(
        name="Base Sepolia",
        chain_id=84532,
        rpc_url=f"https://base-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
        explorer_url="https://sepolia.basescan.org",
        native_token="ETH",
        priority_weight=0.60,
        gas_price_multiplier=1.1,
        max_gas_price_gwei=50.0
    ),
    "arbitrum_sepolia": NetworkConfig(
        name="Arbitrum Sepolia",
        chain_id=421614,
        rpc_url=f"https://arb-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
        explorer_url="https://sepolia.arbiscan.io",
        native_token="ETH",
        priority_weight=0.25,
        gas_price_multiplier=1.15,
        max_gas_price_gwei=100.0
    ),
    "bsc_testnet": NetworkConfig(
        name="BSC Testnet",
        chain_id=97,
        rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545",
        explorer_url="https://testnet.bscscan.com",
        native_token="BNB",
        priority_weight=0.15,
        gas_price_multiplier=1.2,
        max_gas_price_gwei=10.0
    )
}

# ============================================================================
# ENDEREÇOS DE CONTRATOS
# ============================================================================

# AAVE V3 Pool Addresses (para Flash Loans)
AAVE_V3_POOL = {
    # Mainnet
    "base": "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",
    "arbitrum": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
    # BSC não tem Aave V3, usaremos Venus ou PancakeSwap
    "bsc": "0x0000000000000000000000000000000000000000",  # Placeholder
    # Testnets
    "base_sepolia": "0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b",
    "arbitrum_sepolia": "0xBfC91D59fdAA134A4ED45f7B584cAf96D7792Eff",
    "bsc_testnet": "0x0000000000000000000000000000000000000000"  # Placeholder
}

# DEX Router Addresses
UNISWAP_V3_ROUTER = {
    "base": "0x2626664c2603336E57B271c5C0b26F421741e481",
    "arbitrum": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
}

PANCAKESWAP_ROUTER = {
    "bsc": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    "bsc_testnet": "0xD99D1c33F9fC3444f8101754aBC46c52416550D1"
}

AERODROME_ROUTER = {
    "base": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43"
}

# ============================================================================
# PARÂMETROS DO BOT
# ============================================================================

class BotConfig:
    """Configurações gerais do bot"""
    
    # Modo de operação
    USE_TESTNET = os.getenv("USE_TESTNET", "true").lower() == "true"
    
    # Carteira
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
    WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")
    
    # Parâmetros de arbitragem
    MIN_PROFIT_USD = float(os.getenv("MIN_PROFIT_USD", "50"))
    MIN_PROFIT_PERCENTAGE = float(os.getenv("MIN_PROFIT_PERCENTAGE", "1.0"))
    MAX_SLIPPAGE = float(os.getenv("MAX_SLIPPAGE", "0.5"))
    
    # Flash Loan
    FLASH_LOAN_FEE = 0.0009  # 0.09% (Aave V3)
    MIN_FLASH_LOAN_AMOUNT = 10000
    MAX_FLASH_LOAN_AMOUNT = 1000000
    
    # IA e Machine Learning
    ML_CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.80"))
    ML_TRAINING_INTERVAL = int(os.getenv("ML_TRAINING_INTERVAL", "1000"))
    ML_MIN_TRAINING_SAMPLES = int(os.getenv("ML_MIN_TRAINING_SAMPLES", "100"))
    
    # Gestão de capital e proteção contra prejuízo
    MAX_DAILY_GAS_SPEND = float(os.getenv("MAX_DAILY_GAS_SPEND", "5"))  # Máximo $5/dia em gas
    MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", "10"))  # Máximo $10 de perda/dia
    MAX_CONSECUTIVE_FAILURES = int(os.getenv("MAX_CONSECUTIVE_FAILURES", "5"))  # Máx falhas consecutivas
    EMERGENCY_STOP_BALANCE = float(os.getenv("EMERGENCY_STOP_BALANCE", "5"))  # Para se saldo < $5
    REINVEST_PERCENTAGE = float(os.getenv("REINVEST_PERCENTAGE", "0.5"))
    
    # Modo de simulação (DRY RUN)
    DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"  # true = simula sem executar
    SIMULATE_BEFORE_EXECUTE = os.getenv("SIMULATE_BEFORE_EXECUTE", "true").lower() == "true"  # Simular antes
    
    # Monitoramento
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "3"))
    PRICE_UPDATE_INTERVAL = int(os.getenv("PRICE_UPDATE_INTERVAL", "5"))
    RUN_24_7 = os.getenv("RUN_24_7", "true").lower() == "true"
    
    # Dashboard
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "3000"))
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_DIR = os.getenv("LOG_DIR", "data/logs")

# ============================================================================
# TOKENS PARA MONITORAR
# ============================================================================

MAJOR_TOKENS = {
    "USDC": {
        "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "bsc": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
    },
    "USDT": {
        "base": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",
        "arbitrum": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "bsc": "0x55d398326f99059fF775485246999027B3197955"
    },
    "WETH": {
        "base": "0x4200000000000000000000000000000000000006",
        "arbitrum": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    },
    "WBNB": {
        "bsc": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
    }
}

# DEXs para monitorar em cada rede
DEXS_TO_MONITOR = {
    "base": ["uniswap_v3", "aerodrome"],
    "arbitrum": ["uniswap_v3", "camelot", "sushiswap"],
    "bsc": ["pancakeswap_v2", "pancakeswap_v3", "biswap"]
}

# ============================================================================
# VALIDAÇÃO
# ============================================================================

def validate_config():
    """Valida configurações"""
    errors = []
    
    if not BotConfig.PRIVATE_KEY:
        errors.append("PRIVATE_KEY não configurada!")
    
    if not os.getenv("ALCHEMY_API_KEY"):
        errors.append("ALCHEMY_API_KEY não configurada!")
    
    if errors:
        print("❌ ERROS DE CONFIGURAÇÃO:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuração validada!")
    return True

def print_config_summary():
    """Imprime resumo da configuração"""
    mode = "TESTNET" if BotConfig.USE_TESTNET else "MAINNET"
    networks = NETWORKS_TESTNET if BotConfig.USE_TESTNET else NETWORKS_MAINNET
    
    print("\n" + "="*60)
    print(f"🤖 BOT MEV - CONFIGURAÇÃO ({mode})")
    print("="*60)
    print(f"\n📡 Redes:")
    for name, net in networks.items():
        print(f"  • {net.name} - Prioridade: {net.priority_weight*100:.0f}%")
    
    print(f"\n💰 Arbitragem:")
    print(f"  • Lucro mínimo: ${BotConfig.MIN_PROFIT_USD}")
    print(f"  • Diferença mínima: {BotConfig.MIN_PROFIT_PERCENTAGE}%")
    
    print(f"\n🧠 IA: Confiança mínima {BotConfig.ML_CONFIDENCE_THRESHOLD*100:.0f}%")
    print(f"⛽ Gas: Máximo ${BotConfig.MAX_DAILY_GAS_SPEND}/dia")
    print(f"⏰ Operação: 24/7" if BotConfig.RUN_24_7 else "Horários específicos")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    validate_config()
    print_config_summary()
