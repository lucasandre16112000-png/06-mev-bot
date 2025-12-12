"""
🤖 BOT MEV - VERSÃO HÍBRIDA MELHORADA
Flash Loan Arbitrage Bot com IA Adaptativa
FUNCIONA EM TODAS AS REDES (Base, Arbitrum, Ethereum Sepolia)
"""

import sys
import time
import signal
from loguru import logger
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Importar módulos
from src.config.config import BotConfig, validate_config, print_config_summary, convert_native_to_usd
from src.core.blockchain import blockchain
from src.core.dex import MultiDEXScanner

# Usar estratégia HÍBRIDA
from src.strategies.real_flashloan_hybrid import HybridFlashLoanStrategy

# Usar IA avançada se disponível
try:
    from src.ai.advanced_ml_engine import AdvancedMLEngine as MLEngine
    logger.info("✅ Usando AdvancedMLEngine (IA TURBINADA)")
except ImportError:
    from src.ai.ml_engine import MLEngine
    logger.info("✅ Usando MLEngine (IA BÁSICA)")

from src.utils.risk_manager import RiskManager

class MEVBotHybrid:
    """Bot MEV Híbrido - Funciona em todas as redes"""
    
    def __init__(self):
        self.running = False
        self.blockchain = blockchain
        self.dex_scanner = None
        self.flash_loan_strategy = None
        self.ml_engine = None
        self.risk_manager = RiskManager()
        self.stats = {
            'start_time': time.time(),
            'cycles': 0,
            'opportunities_found': 0,
            'trades_executed': 0,
            'total_profit': 0.0,
            'total_gas_spent': 0.0
        }
        
        # Configurar signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de interrupção"""
        logger.warning("\n⚠️ Sinal de interrupção recebido!")
        self.stop()
    
    def initialize(self) -> bool:
        """Inicializa todos os componentes do bot"""
        try:
            self._print_banner()
            
            logger.info("🚀 Inicializando BOT MEV HÍBRIDO...")
            
            # Validar configuração
            if not validate_config():
                logger.error("❌ Configuração inválida!")
                return False
            
            print_config_summary()
            
            # Modo de operação
            if BotConfig.USE_TESTNET:
                logger.info("🧪 MODO TESTNET HÍBRIDO - Funciona em todas as redes!")
            else:
                logger.warning("💰 MODO MAINNET - Transações reais com dinheiro de verdade!")
            
            if BotConfig.DRY_RUN:
                logger.warning("🎭 MODO DRY RUN - Nenhuma transação real será executada!")
            else:
                logger.warning("💰 MODO REAL - Transações serão EXECUTADAS")
            
            # Inicializar blockchain
            logger.info("🔗 Conectando blockchains...")
            if not self.blockchain.initialize():
                logger.error("❌ Falha ao conectar blockchains!")
                return False
            
            # Inicializar DEX scanner
            logger.info("🔍 Inicializando scanner de DEXs...")
            self.dex_scanner = MultiDEXScanner(self.blockchain)
            
            # Inicializar estratégia de flash loan HÍBRIDA
            logger.info("⚡ Inicializando estratégia Flash Loan HÍBRIDA...")
            self.flash_loan_strategy = HybridFlashLoanStrategy(
                self.blockchain,
                self.dex_scanner
            )
            
            # Inicializar IA
            logger.info("🧠 Inicializando Motor de IA...")
            self.ml_engine = MLEngine()
            
            # Inicializar Risk Manager
            logger.info("🛡️ Inicializando Risk Manager...")
            logger.info("  ✅ Simulação antes de executar: ATIVA")
            logger.info("  ✅ Limite de perda diária: $" + str(BotConfig.MAX_DAILY_LOSS))
            logger.info("  ✅ Limite de gas diário: $" + str(BotConfig.MAX_DAILY_GAS_SPEND))
            logger.info("  ✅ Circuit breaker: ATIVO")
            
            logger.success("✅ Bot híbrido inicializado com sucesso!")
            logger.success("🎯 Pronto para operar em Base, Arbitrum e Ethereum Sepolia!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Loop principal do bot"""
        try:
            self.running = True
            logger.success("🎯 BOT HÍBRIDO INICIADO! Rodando 24/7...")
            logger.info(f"⏱️ Intervalo de checagem: {BotConfig.CHECK_INTERVAL_SECONDS}s")
            
            while self.running:
                try:
                    self.stats['cycles'] += 1
                    
                    # Verificar saúde das conexões
                    if self.stats['cycles'] % 100 == 0:
                        self._check_health()
                        self.risk_manager.print_stats()
                    
                    # Buscar e executar oportunidades
                    self._execute_cycle()
                    
                    # Aguardar próximo ciclo
                    time.sleep(BotConfig.CHECK_INTERVAL_SECONDS)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"❌ Erro no ciclo: {e}")
                    time.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
        finally:
            self.stop()
    
    def _execute_cycle(self):
        """Executa um ciclo de busca e execução"""
        try:
            # Buscar oportunidade
            result = self.flash_loan_strategy.find_and_execute()
            
            if result:
                self.stats['trades_executed'] += 1
                
                opportunity = result['opportunity']
                profit = result['profit']
                
                # Registrar na IA
                success = profit.get('profitable', False)
                actual_profit = profit.get('net_profit_usd', 0)
                
                self.ml_engine.record_result(opportunity, success, actual_profit)
                
                if success:
                    self.stats['total_profit'] += actual_profit
                    logger.success(f"💰 Lucro acumulado: ${self.stats['total_profit']:.2f}")
                
                # Exibir estatísticas periodicamente
                if self.stats['trades_executed'] % 10 == 0:
                    self._print_stats()
            
            # Verificar se deve parar (saldo baixo)
            self._check_emergency_stop()
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo de execução: {e}")
    
    def _check_health(self):
        """Verifica saúde das conexões"""
        try:
            health = self.blockchain.check_health()
            
            unhealthy = [net for net, status in health.items() if not status]
            
            if unhealthy:
                logger.warning(f"⚠️ Redes com problema: {unhealthy}")
                
                # Tentar reconectar
                for network in unhealthy:
                    logger.info(f"🔄 Reconectando {network}...")
                    self.blockchain.reconnect(network)
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saúde: {e}")
    
    def _check_emergency_stop(self):
        """Verifica se deve parar por saldo baixo"""
        try:
            for network_name in self.blockchain.web3_instances.keys():
                balance = self.blockchain.get_balance(network_name)
                
                if balance < BotConfig.EMERGENCY_STOP_BALANCE:
                    balance_usd = convert_native_to_usd(balance, network_name)
                    min_usd = convert_native_to_usd(BotConfig.EMERGENCY_STOP_BALANCE, network_name)
                    
                    logger.error(f"🛑 EMERGÊNCIA: Saldo baixo em {network_name}!")
                    logger.error(f"   Saldo atual: {balance:.6f} (~${balance_usd:.2f})")
                    logger.error(f"   Mínimo: {BotConfig.EMERGENCY_STOP_BALANCE} (~${min_usd:.2f})")
                    logger.error("   Bot será pausado!")
                    self.stop()
                    return
        
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saldo: {e}")
    
    def _print_stats(self):
        """Imprime estatísticas do bot"""
        try:
            uptime = time.time() - self.stats['start_time']
            hours = uptime / 3600
            
            logger.info("\n" + "="*60)
            logger.info(f"{Fore.CYAN}📊 ESTATÍSTICAS DO BOT HÍBRIDO")
            logger.info("="*60)
            logger.info(f"⏱️ Uptime: {hours:.2f} horas")
            logger.info(f"🔄 Ciclos executados: {self.stats['cycles']:,}")
            logger.info(f"🎯 Oportunidades encontradas: {self.stats['opportunities_found']}")
            logger.info(f"⚡ Trades executados: {self.stats['trades_executed']}")
            logger.info(f"💰 Lucro total: ${self.stats['total_profit']:.2f}")
            logger.info(f"⛽ Gas gasto: ${self.stats['total_gas_spent']:.2f}")
            
            # Stats da IA
            ml_stats = self.ml_engine.get_performance_stats()
            logger.info(f"🧠 IA treinada: {'Sim' if ml_stats.get('is_trained') else 'Não'}")
            logger.info(f"📈 Taxa de sucesso: {ml_stats.get('success_rate', 0):.1f}%")
            
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Erro ao imprimir stats: {e}")
    
    def stop(self):
        """Para o bot"""
        if not self.running:
            return
        
        logger.warning("🛑 Parando bot híbrido...")
        self.running = False
        
        # Imprimir estatísticas finais
        self._print_stats()
        
        # Fechar conexões
        if self.blockchain:
            self.blockchain.close_all()
        
        logger.info("👋 Bot encerrado!")
        sys.exit(0)
    
    def _print_banner(self):
        """Imprime banner do bot"""
        banner = f"""
{Fore.CYAN}{'='*60}
{Fore.GREEN}
    ███╗   ███╗███████╗██╗   ██╗    ██████╗  ██████╗ ████████╗
    ████╗ ████║██╔════╝██║   ██║    ██╔══██╗██╔═══██╗╚══██╔══╝
    ██╔████╔██║█████╗  ██║   ██║    ██████╔╝██║   ██║   ██║   
    ██║╚██╔╝██║██╔══╝  ╚██╗ ██╔╝    ██╔══██╗██║   ██║   ██║   
    ██║ ╚═╝ ██║███████╗ ╚████╔╝     ██████╔╝╚██████╔╝   ██║   
    ╚═╝     ╚═╝╚══════╝  ╚═══╝      ╚═════╝  ╚═════╝    ╚═╝   
{Fore.YELLOW}
    🚀 VERSÃO HÍBRIDA - 100% FUNCIONAL EM TODAS AS REDES 🚀
    Flash Loan Arbitrage Bot com IA Adaptativa
    Base, Arbitrum e Ethereum Sepolia
    
    ✅ Smart Contracts HÍBRIDOS
    ✅ Funciona COM ou SEM Uniswap
    ✅ IA Turbinada (5 modelos)
    ✅ Anti-Scam REAL (7 verificações)
    ✅ Execução REAL na blockchain
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
        """
        print(banner)

def main():
    """Função principal"""
    try:
        # Criar e inicializar bot
        bot = MEVBotHybrid()
        
        if not bot.initialize():
            logger.error("❌ Falha na inicialização!")
            sys.exit(1)
        
        # Rodar bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Interrompido pelo usuário!")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
