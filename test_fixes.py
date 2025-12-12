"""
🧪 SCRIPT DE TESTE - Valida todas as correções
"""

import sys
from loguru import logger
from colorama import init, Fore, Style

init(autoreset=True)

def test_imports():
    """Testa se todos os imports funcionam"""
    logger.info("🧪 Testando imports...")
    
    try:
        from src.config.config import (
            BotConfig, 
            validate_config, 
            print_config_summary,
            convert_native_to_usd,
            convert_usd_to_native,
            get_native_token_price
        )
        logger.success("  ✅ Config imports OK")
    except Exception as e:
        logger.error(f"  ❌ Config imports FALHOU: {e}")
        return False
    
    try:
        from src.core.blockchain import blockchain
        logger.success("  ✅ Blockchain import OK")
    except Exception as e:
        logger.error(f"  ❌ Blockchain import FALHOU: {e}")
        return False
    
    try:
        from web3.middleware import geth_poa_middleware
        logger.success("  ✅ POA Middleware import OK")
    except Exception as e:
        logger.error(f"  ❌ POA Middleware import FALHOU: {e}")
        return False
    
    return True


def test_config():
    """Testa configurações"""
    logger.info("\n🧪 Testando configurações...")
    
    try:
        from src.config.config import (
            BotConfig,
            validate_config,
            convert_native_to_usd,
            convert_usd_to_native
        )
        
        # Testar EMERGENCY_STOP_BALANCE
        logger.info(f"  📊 EMERGENCY_STOP_BALANCE: {BotConfig.EMERGENCY_STOP_BALANCE} ETH")
        
        if BotConfig.EMERGENCY_STOP_BALANCE > 1.0:
            logger.error(f"  ❌ EMERGENCY_STOP_BALANCE muito alto! ({BotConfig.EMERGENCY_STOP_BALANCE})")
            logger.error("     Deveria ser algo como 0.001-0.01 ETH")
            return False
        
        logger.success(f"  ✅ EMERGENCY_STOP_BALANCE correto!")
        
        # Testar conversões
        test_amount = 0.02  # 0.02 ETH
        usd_value = convert_native_to_usd(test_amount, "arbitrum_sepolia")
        logger.info(f"  💰 0.02 ETH = ${usd_value:.2f} USD")
        
        if usd_value < 10 or usd_value > 200:
            logger.warning(f"  ⚠️ Conversão USD parece estranha: ${usd_value}")
        else:
            logger.success(f"  ✅ Conversão USD OK")
        
        # Validar config
        if not validate_config():
            logger.error("  ❌ Validação de config FALHOU")
            return False
        
        logger.success("  ✅ Configuração válida!")
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Erro ao testar config: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_connections():
    """Testa conexões blockchain"""
    logger.info("\n🧪 Testando conexões blockchain...")
    
    try:
        from src.core.blockchain import blockchain
        
        logger.info("  🔌 Inicializando conexões...")
        
        if not blockchain.initialize():
            logger.error("  ❌ Falha ao inicializar blockchain")
            return False
        
        logger.success(f"  ✅ Conectado em {len(blockchain.web3_instances)} redes!")
        
        # Testar cada rede
        for network_name, w3 in blockchain.web3_instances.items():
            try:
                block = w3.eth.block_number
                balance = blockchain.get_balance(network_name)
                
                logger.info(f"  📡 {network_name}:")
                logger.info(f"     Bloco: {block:,}")
                logger.info(f"     Saldo: {balance:.6f}")
                
                # Testar conversão USD
                from src.config.config import convert_native_to_usd
                balance_usd = convert_native_to_usd(balance, network_name)
                logger.info(f"     Saldo USD: ${balance_usd:.2f}")
                
            except Exception as e:
                logger.error(f"  ❌ Erro em {network_name}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Erro ao testar conexões: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_emergency_stop_logic():
    """Testa lógica de emergency stop"""
    logger.info("\n🧪 Testando lógica de emergency stop...")
    
    try:
        from src.config.config import BotConfig, convert_native_to_usd
        
        # Simular saldos
        test_cases = [
            ("arbitrum_sepolia", 0.02, "DEVE PASSAR"),
            ("arbitrum_sepolia", 0.0005, "DEVE PARAR"),
            ("bsc_testnet", 0.3, "DEVE PASSAR"),
            ("bsc_testnet", 0.0005, "DEVE PARAR"),
        ]
        
        for network, balance, expected in test_cases:
            should_stop = balance < BotConfig.EMERGENCY_STOP_BALANCE
            balance_usd = convert_native_to_usd(balance, network)
            
            status = "🛑 PARA" if should_stop else "✅ OK"
            logger.info(f"  {status} {network}: {balance:.6f} (~${balance_usd:.2f}) - {expected}")
            
            if expected == "DEVE PARAR" and not should_stop:
                logger.error(f"    ❌ ERRO: Deveria parar mas não parou!")
                return False
            
            if expected == "DEVE PASSAR" and should_stop:
                logger.error(f"    ❌ ERRO: Não deveria parar mas parou!")
                return False
        
        logger.success("  ✅ Lógica de emergency stop correta!")
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Erro ao testar emergency stop: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dex_addresses():
    """Testa se endereços de DEXs estão configurados"""
    logger.info("\n🧪 Testando endereços de DEXs...")
    
    try:
        from src.config.config import (
            UNISWAP_V3_ROUTER,
            PANCAKESWAP_V3_ROUTER,
            AERODROME_ROUTER,
            CAMELOT_ROUTER,
            TOKENS
        )
        
        logger.info("  📍 Uniswap V3 Router:")
        for network, address in UNISWAP_V3_ROUTER.items():
            if address != "0x0000000000000000000000000000000000000000":
                logger.success(f"    ✅ {network}: {address[:10]}...")
            else:
                logger.warning(f"    ⚠️ {network}: Não disponível")
        
        logger.info("  📍 PancakeSwap V3 Router:")
        for network, address in PANCAKESWAP_V3_ROUTER.items():
            if address != "0x0000000000000000000000000000000000000000":
                logger.success(f"    ✅ {network}: {address[:10]}...")
        
        logger.info("  📍 Tokens configurados:")
        for network, tokens in TOKENS.items():
            logger.info(f"    {network}: {len(tokens)} tokens")
            for symbol, address in tokens.items():
                logger.info(f"      • {symbol}: {address[:10]}...")
        
        logger.success("  ✅ Endereços de DEXs configurados!")
        return True
        
    except Exception as e:
        logger.error(f"  ❌ Erro ao testar DEXs: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}🧪 TESTE DE CORREÇÕES - BOT MEV")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configurações", test_config),
        ("Conexões Blockchain", test_connections),
        ("Lógica Emergency Stop", test_emergency_stop_logic),
        ("Endereços DEXs", test_dex_addresses),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Erro fatal em {test_name}: {e}")
            results[test_name] = False
    
    # Resumo
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}📊 RESUMO DOS TESTES")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Fore.GREEN}✅ PASSOU" if result else f"{Fore.RED}❌ FALHOU"
        print(f"  {status}{Style.RESET_ALL} - {test_name}")
    
    print(f"\n{Fore.CYAN}{'='*60}")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 TODOS OS TESTES PASSARAM! ({passed}/{total})")
        print(f"{Fore.GREEN}✅ Bot está pronto para rodar!")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"{Fore.RED}❌ ALGUNS TESTES FALHARAM! ({passed}/{total})")
        print(f"{Fore.RED}⚠️ Corrija os erros antes de rodar o bot!")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
