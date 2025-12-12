"""
🧪 TESTE DE IMPORTS - Verifica se todos os módulos podem ser importados
"""

import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, '/home/ubuntu/mev-bot-pro')

def test_imports():
    """Testa todos os imports"""
    results = {}
    
    # Teste 1: Config
    print("🧪 Testando imports de config...")
    try:
        from src.config.config import (
            BotConfig,
            NETWORKS_TESTNET,
            NETWORKS_MAINNET,
            AAVE_V3_POOL,
            UNISWAP_V3_ROUTER,
            PANCAKESWAP_V3_ROUTER,
            TOKENS,
            convert_native_to_usd,
            convert_usd_to_native,
            get_native_token_price,
            validate_config,
            print_config_summary
        )
        print("  ✅ Config: OK")
        results['config'] = True
    except Exception as e:
        print(f"  ❌ Config: ERRO - {e}")
        results['config'] = False
    
    # Teste 2: Blockchain
    print("\n🧪 Testando imports de blockchain...")
    try:
        from src.core.blockchain import BlockchainConnector
        print("  ✅ Blockchain: OK")
        results['blockchain'] = True
    except Exception as e:
        print(f"  ❌ Blockchain: ERRO - {e}")
        results['blockchain'] = False
    
    # Teste 3: DEX
    print("\n🧪 Testando imports de DEX...")
    try:
        from src.core.dex import DEXInterface, MultiDEXScanner
        print("  ✅ DEX: OK")
        results['dex'] = True
    except Exception as e:
        print(f"  ❌ DEX: ERRO - {e}")
        results['dex'] = False
    
    # Teste 4: Flash Loan Real
    print("\n🧪 Testando imports de Flash Loan Real...")
    try:
        from src.strategies.real_flashloan import RealFlashLoanExecutor, RealFlashLoanStrategy
        print("  ✅ Flash Loan Real: OK")
        results['real_flashloan'] = True
    except Exception as e:
        print(f"  ❌ Flash Loan Real: ERRO - {e}")
        results['real_flashloan'] = False
    
    # Teste 5: Flash Loan Básico (fallback)
    print("\n🧪 Testando imports de Flash Loan Básico...")
    try:
        from src.strategies.flashloan import FlashLoanExecutor, FlashLoanStrategy
        print("  ✅ Flash Loan Básico: OK")
        results['flashloan'] = True
    except Exception as e:
        print(f"  ❌ Flash Loan Básico: ERRO - {e}")
        results['flashloan'] = False
    
    # Teste 6: IA Avançada
    print("\n🧪 Testando imports de IA Avançada...")
    try:
        from src.ai.advanced_ml_engine import AdvancedMLEngine
        print("  ✅ IA Avançada: OK")
        results['advanced_ml'] = True
    except Exception as e:
        print(f"  ❌ IA Avançada: ERRO - {e}")
        results['advanced_ml'] = False
    
    # Teste 7: IA Básica (fallback)
    print("\n🧪 Testando imports de IA Básica...")
    try:
        from src.ai.ml_engine import MLEngine
        print("  ✅ IA Básica: OK")
        results['ml_engine'] = True
    except Exception as e:
        print(f"  ❌ IA Básica: ERRO - {e}")
        results['ml_engine'] = False
    
    # Teste 8: Token Security Real
    print("\n🧪 Testando imports de Token Security Real...")
    try:
        from src.utils.real_token_security import RealTokenSecurity
        print("  ✅ Token Security Real: OK")
        results['real_token_security'] = True
    except Exception as e:
        print(f"  ❌ Token Security Real: ERRO - {e}")
        results['real_token_security'] = False
    
    # Teste 9: Token Security Básico (fallback)
    print("\n🧪 Testando imports de Token Security Básico...")
    try:
        from src.utils.advanced_token_security import AdvancedTokenSecurity
        print("  ✅ Token Security Básico: OK")
        results['token_security'] = True
    except Exception as e:
        print(f"  ❌ Token Security Básico: ERRO - {e}")
        results['token_security'] = False
    
    # Teste 10: Risk Manager
    print("\n🧪 Testando imports de Risk Manager...")
    try:
        from src.utils.risk_manager import RiskManager
        print("  ✅ Risk Manager: OK")
        results['risk_manager'] = True
    except Exception as e:
        print(f"  ❌ Risk Manager: ERRO - {e}")
        results['risk_manager'] = False
    
    return results


def test_config_values():
    """Testa valores de configuração"""
    print("\n" + "="*60)
    print("🧪 TESTANDO VALORES DE CONFIGURAÇÃO")
    print("="*60)
    
    try:
        from src.config.config import BotConfig, convert_native_to_usd
        
        # Teste EMERGENCY_STOP_BALANCE
        print(f"\n📊 EMERGENCY_STOP_BALANCE: {BotConfig.EMERGENCY_STOP_BALANCE}")
        if BotConfig.EMERGENCY_STOP_BALANCE > 1.0:
            print("  ❌ ERRO: Valor muito alto! Deveria ser ~0.001-0.01")
            return False
        else:
            print("  ✅ OK: Valor correto")
        
        # Teste conversão USD
        test_balance = 0.02
        usd = convert_native_to_usd(test_balance, "arbitrum_sepolia")
        print(f"\n💰 Conversão USD: {test_balance} ETH = ${usd:.2f}")
        if usd < 10 or usd > 200:
            print("  ⚠️ AVISO: Valor parece estranho")
        else:
            print("  ✅ OK: Conversão razoável")
        
        # Teste MIN_PROFIT
        print(f"\n💵 MIN_PROFIT_USD: ${BotConfig.MIN_PROFIT_USD}")
        print(f"📈 MIN_PROFIT_PERCENTAGE: {BotConfig.MIN_PROFIT_PERCENTAGE}%")
        
        if BotConfig.MIN_PROFIT_USD > 50:
            print("  ⚠️ AVISO: Valor alto para testnet")
        else:
            print("  ✅ OK: Valor adequado para testnet")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao testar config: {e}")
        return False


def main():
    """Função principal"""
    print("="*60)
    print("🧪 TESTE DE IMPORTS E CONFIGURAÇÕES")
    print("="*60)
    
    # Testar imports
    results = test_imports()
    
    # Testar configurações
    config_ok = test_config_values()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for module, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {module}")
    
    print(f"\n  Config values: {'✅' if config_ok else '❌'}")
    
    print("\n" + "="*60)
    
    if passed == total and config_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print(f"✅ {passed}/{total} módulos OK")
        print("✅ Configurações OK")
        return 0
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print(f"⚠️ {passed}/{total} módulos OK")
        if not config_ok:
            print("❌ Configurações com problema")
        return 1


if __name__ == "__main__":
    sys.exit(main())
