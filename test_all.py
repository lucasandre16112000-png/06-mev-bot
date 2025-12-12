"""
🧪 SCRIPT DE TESTE COMPLETO
Testa TODAS as funcionalidades do bot
"""

import sys
from loguru import logger
from colorama import init, Fore, Style

init(autoreset=True)

def print_section(title):
    """Imprime seção de teste"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}{title}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def test_imports():
    """Teste 1: Importações"""
    print_section("TESTE 1: IMPORTAÇÕES")
    
    try:
        from web3 import Web3
        logger.success("✅ Web3 importado")
        
        from src.config.config import BotConfig
        logger.success("✅ Config importado")
        
        from src.core.blockchain import blockchain
        logger.success("✅ Blockchain importado")
        
        from src.utils.advanced_token_security import AdvancedTokenSecurity
        logger.success("✅ Token Security importado")
        
        from src.utils.risk_manager import RiskManager
        logger.success("✅ Risk Manager importado")
        
        from src.ai.ml_engine import MLEngine
        logger.success("✅ ML Engine importado")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def test_config():
    """Teste 2: Configuração"""
    print_section("TESTE 2: CONFIGURAÇÃO")
    
    try:
        from src.config.config import BotConfig, validate_config
        
        # Validar config
        if not validate_config():
            logger.error("❌ Configuração inválida")
            return False
        
        logger.success("✅ Configuração válida")
        
        # Verificar valores
        logger.info(f"  Lucro mínimo: ${BotConfig.MIN_PROFIT_USD}")
        logger.info(f"  Diferença mínima: {BotConfig.MIN_PROFIT_PERCENTAGE}%")
        logger.info(f"  Max gas/dia: ${BotConfig.MAX_DAILY_GAS_SPEND}")
        logger.info(f"  Max perda/dia: ${BotConfig.MAX_DAILY_LOSS}")
        logger.info(f"  Testnet: {BotConfig.USE_TESTNET}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def test_blockchain():
    """Teste 3: Conexões Blockchain"""
    print_section("TESTE 3: CONEXÕES BLOCKCHAIN")
    
    try:
        from src.core.blockchain import blockchain
        
        # Inicializar
        if not blockchain.initialize():
            logger.error("❌ Falha ao inicializar blockchain")
            return False
        
        logger.success("✅ Blockchain inicializado")
        
        # Verificar redes conectadas
        networks = blockchain.get_connected_networks()
        logger.info(f"  Redes conectadas: {len(networks)}")
        
        for network in networks:
            logger.success(f"  ✅ {network}")
        
        # Verificar saldos
        for network in networks:
            balance = blockchain.get_balance(network)
            logger.info(f"  Saldo {network}: {balance:.6f}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return False

def test_token_security():
    """Teste 4: Sistema Anti-Scam"""
    print_section("TESTE 4: SISTEMA ANTI-SCAM")
    
    try:
        from web3 import Web3
        from src.utils.advanced_token_security import AdvancedTokenSecurity
        
        # Criar instância
        w3 = Web3(Web3.HTTPProvider('https://arb-sepolia.g.alchemy.com/v2/Zbk6gec3x6CTvSKTyxg3I'))
        security = AdvancedTokenSecurity(w3, 'arbitrum')
        
        logger.info("Testando verificações...")
        
        # Teste 1: Token whitelist (deve passar)
        usdc = '0xaf88d065e77c8cC2239327C5EDb3A432268e5831'
        is_safe, reason = security.is_token_safe(usdc)
        
        if is_safe:
            logger.success(f"✅ USDC aprovado: {reason}")
        else:
            logger.error(f"❌ USDC rejeitado: {reason}")
            return False
        
        # Teste 2: Endereço inválido (deve falhar)
        fake = '0x0000000000000000000000000000000000000001'
        is_safe, reason = security.is_token_safe(fake)
        
        if not is_safe:
            logger.success(f"✅ Endereço fake rejeitado: {reason}")
        else:
            logger.error(f"❌ Endereço fake aprovado (ERRO!)")
            return False
        
        # Teste 3: Verificar configurações
        logger.info(f"  Liquidez mínima: ${security.MIN_LIQUIDITY_USD:,}")
        logger.info(f"  Volume mínimo: ${security.MIN_VOLUME_24H_USD:,}")
        logger.info(f"  Idade mínima: {security.MIN_CONTRACT_AGE_DAYS} dias")
        logger.info(f"  Holders mínimos: {security.MIN_HOLDERS}")
        
        # Teste 4: Score de segurança
        score = security.get_security_score(usdc)
        logger.info(f"  Score USDC: {score}/100")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_risk_manager():
    """Teste 5: Risk Manager"""
    print_section("TESTE 5: RISK MANAGER")
    
    try:
        from src.utils.risk_manager import RiskManager
        
        # Criar instância
        rm = RiskManager()
        logger.success("✅ Risk Manager criado")
        
        # Teste 1: Pode executar?
        can_execute, reason = rm.can_execute_trade(0.50)
        
        if can_execute:
            logger.success(f"✅ Pode executar: {reason}")
        else:
            logger.error(f"❌ Não pode executar: {reason}")
            return False
        
        # Teste 2: Registrar trades
        logger.info("Simulando trades...")
        
        rm.record_trade_result(success=True, profit=100.0, gas_cost=0.50)
        logger.success("  ✅ Trade 1: +$100")
        
        rm.record_trade_result(success=True, profit=50.0, gas_cost=0.30)
        logger.success("  ✅ Trade 2: +$50")
        
        rm.record_trade_result(success=False, profit=-10.0, gas_cost=0.20)
        logger.warning("  ❌ Trade 3: -$10")
        
        # Teste 3: Verificar stats
        rm.print_stats()
        
        # Teste 4: Verificar proteções
        if rm.emergency_stop:
            logger.error("❌ Emergency stop ativado (não deveria)")
            return False
        else:
            logger.success("✅ Emergency stop OK")
        
        if rm.consecutive_failures >= rm.max_consecutive_failures:
            logger.error("❌ Circuit breaker ativado (não deveria)")
            return False
        else:
            logger.success("✅ Circuit breaker OK")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_engine():
    """Teste 6: Motor de IA"""
    print_section("TESTE 6: MOTOR DE IA")
    
    try:
        from src.ai.ml_engine import MLEngine
        
        # Criar instância
        ml = MLEngine()
        logger.success("✅ ML Engine criado")
        
        # Teste 1: Verificar estado inicial
        stats = ml.get_performance_stats()
        logger.info(f"  Treinado: {stats.get('is_trained', False)}")
        logger.info(f"  Taxa de sucesso: {stats.get('success_rate', 0):.1f}%")
        
        # Teste 2: Simular dados de treinamento
        logger.info("Simulando treinamento...")
        
        from datetime import datetime
        
        for i in range(10):
            opportunity = {
                'profit_estimate': 50 + i * 10,
                'profit_percentage': 1.0 + i * 0.5,
                'gas_cost': 0.5,
                'dex_from': 'uniswap',
                'dex_to': 'aerodrome',
                'network': 'base',
                'timestamp': datetime.now()
            }
            
            success = i % 3 != 0  # 66% de sucesso
            actual_profit = opportunity['profit_estimate'] if success else -10
            
            ml.record_result(opportunity, success, actual_profit)
        
        logger.success("✅ 10 trades simulados registrados")
        
        # Teste 3: Verificar stats atualizados
        stats = ml.get_performance_stats()
        logger.info(f"  Treinado: {stats.get('is_trained', False)}")
        logger.info(f"  Taxa de sucesso: {stats.get('success_rate', 0):.1f}%")
        logger.info(f"  Total trades: {stats.get('total_trades', 0)}")
        
        # Teste 4: Fazer predição
        test_opportunity = {
            'profit_estimate': 100,
            'profit_percentage': 2.0,
            'gas_cost': 0.5,
            'dex_from': 'uniswap',
            'dex_to': 'aerodrome',
            'network': 'base',
            'timestamp': datetime.now()
        }
        
        should_execute, confidence = ml.should_execute(test_opportunity)
        logger.info(f"  Predição: {should_execute}")
        logger.info(f"  Confiança: {confidence:.1%}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_initialization():
    """Teste 7: Inicialização do Bot"""
    print_section("TESTE 7: INICIALIZAÇÃO DO BOT")
    
    try:
        from main import MEVBot
        
        # Criar bot
        logger.info("Criando bot...")
        bot = MEVBot()
        logger.success("✅ Bot criado")
        
        # Inicializar
        logger.info("Inicializando bot...")
        if not bot.initialize():
            logger.error("❌ Falha ao inicializar bot")
            return False
        
        logger.success("✅ Bot inicializado com sucesso!")
        
        # Verificar componentes
        if bot.blockchain:
            logger.success("  ✅ Blockchain OK")
        else:
            logger.error("  ❌ Blockchain não inicializado")
            return False
        
        if bot.dex_scanner:
            logger.success("  ✅ DEX Scanner OK")
        else:
            logger.error("  ❌ DEX Scanner não inicializado")
            return False
        
        if bot.flash_loan_strategy:
            logger.success("  ✅ Flash Loan Strategy OK")
        else:
            logger.error("  ❌ Flash Loan Strategy não inicializado")
            return False
        
        if bot.ml_engine:
            logger.success("  ✅ ML Engine OK")
        else:
            logger.error("  ❌ ML Engine não inicializado")
            return False
        
        if bot.risk_manager:
            logger.success("  ✅ Risk Manager OK")
        else:
            logger.error("  ❌ Risk Manager não inicializado")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar todos os testes"""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{Fore.CYAN}🧪 TESTE COMPLETO DO BOT MEV")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
    
    results = []
    
    # Executar testes
    results.append(("Importações", test_imports()))
    results.append(("Configuração", test_config()))
    results.append(("Blockchain", test_blockchain()))
    results.append(("Anti-Scam", test_token_security()))
    results.append(("Risk Manager", test_risk_manager()))
    results.append(("ML Engine", test_ml_engine()))
    results.append(("Bot Completo", test_bot_initialization()))
    
    # Resumo
    print_section("RESUMO DOS TESTES")
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            logger.success(f"✅ {name}: PASSOU")
            passed += 1
        else:
            logger.error(f"❌ {name}: FALHOU")
            failed += 1
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}RESULTADO FINAL:")
    print(f"{Fore.GREEN}  ✅ Testes passados: {passed}/{len(results)}")
    print(f"{Fore.RED}  ❌ Testes falhados: {failed}/{len(results)}")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 TODOS OS TESTES PASSARAM! BOT 100% FUNCIONAL!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"\n{Fore.RED}❌ ALGUNS TESTES FALHARAM! VERIFIQUE OS ERROS ACIMA.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
