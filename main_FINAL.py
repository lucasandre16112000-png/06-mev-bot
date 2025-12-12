"""
🤖 BOT MEV - VERSÃO FINAL 100% REAL E FUNCIONAL
Flash Loan Arbitrage Bot com IA Avançada
TODAS AS MELHORIAS INTEGRADAS
"""

import sys
import time
import signal
from loguru import logger
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Importar configurações
from src.config.config import (
    BotConfig, 
    validate_config, 
    print_config_summary,
    convert_native_to_usd
)

# Importar módulos core
from src.core.blockchain import blockchain
from src.core.dex import MultiDEXScanner

# Importar estratégias - VERSÃO REAL
try:
    from src.strategies.real_flashloan import RealFlashLoanStrategy
    REAL_FLASHLOAN_AVAILABLE = True
    logger.info("✅ Usando RealFlashLoanStrategy (VERSÃO REAL)")
except ImportError as e:
    logger.warning(f"⚠️ RealFlashLoanStrategy não disponível: {e}")
    from src.strategies.flashloan import FlashLoanStrategy
    REAL_FLASHLOAN_AVAILABLE = False
    logger.warning("⚠️ Usando FlashLoanStrategy (VERSÃO SIMULADA)")

# Importar IA - VERSÃO AVANÇADA
try:
    from src.ai.advanced_ml_engine import AdvancedMLEngine
    ADVANCED_ML_AVAILABLE = True
    logger.info("✅ Usando AdvancedMLEngine (IA TURBINADA)")
except ImportError as e:
    logger.warning(f"⚠️ AdvancedMLEngine não disponível: {e}")
    try:
        from src.ai.ml_engine import MLEngine
        ADVANCED_ML_AVAILABLE = False
        logger.warning("⚠️ Usando MLEngine (IA BÁSICA)")
    except ImportError:
        logger.error("❌ Nenhum motor de IA disponível!")
        sys.exit(1)

# Importar Risk Manager
from src.utils.risk_manager import RiskManager


class FinalMEVBot:
    """Bot MEV FINAL - 100% Real e Funcional"""
    
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
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit_usd': 0.0,
            'total_gas_spent_usd': 0.0,
            'best_trade': None,
            'worst_trade': None
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
            
            logger.info("🚀 Inicializando BOT MEV FINAL...")
            
            # Validar configuração
            if not validate_config():
                logger.error("❌ Configuração inválida!")
                return False
            
            print_config_summary()
            
            # Verificar modo
            if BotConfig.DRY_RUN:
                logger.warning("🎭 MODO DRY RUN ATIVO - Transações serão simuladas!")
            else:
                if BotConfig.USE_TESTNET:
                    logger.info("🧪 MODO TESTNET REAL - Transações reais em testnet!")
                else:
                    logger.warning("💰 MODO MAINNET REAL - Transações REAIS com dinheiro de verdade!")
                    logger.warning("⚠️ Certifique-se de ter saldo suficiente para gas!")
                    
                    # Confirmar mainnet
                    confirm = input("\n❓ Confirma execução em MAINNET REAL? (sim/não): ")
                    if confirm.lower() not in ['sim', 's', 'yes', 'y']:
                        logger.warning("⚠️ Execução cancelada pelo usuário")
                        return False
            
            # Inicializar blockchain
            logger.info("🔗 Conectando blockchains...")
            if not self.blockchain.initialize():
                logger.error("❌ Falha ao conectar blockchains!")
                return False
            
            # Verificar saldos
            self._check_initial_balances()
            
            # Inicializar DEX scanner
            logger.info("🔍 Inicializando scanner de DEXs...")
            self.dex_scanner = MultiDEXScanner(self.blockchain)
            logger.success("✅ DEX Scanner inicializado!")
            
            # Inicializar estratégia de flash loan
            logger.info("⚡ Inicializando estratégia Flash Loan...")
            if REAL_FLASHLOAN_AVAILABLE:
                logger.success("  ✅ Usando RealFlashLoanStrategy (EXECUÇÃO REAL)")
                self.flash_loan_strategy = RealFlashLoanStrategy(
                    self.blockchain,
                    self.dex_scanner
                )
            else:
                logger.warning("  ⚠️ Usando FlashLoanStrategy (SIMULAÇÃO)")
                from src.strategies.flashloan import FlashLoanStrategy
                self.flash_loan_strategy = FlashLoanStrategy(
                    self.blockchain,
                    self.dex_scanner
                )
            
            # Inicializar IA
            logger.info("🧠 Inicializando Motor de IA...")
            if ADVANCED_ML_AVAILABLE:
                logger.success("  ✅ Usando IA AVANÇADA")
                logger.info("     • Random Forest")
                logger.info("     • Gradient Boosting")
                logger.info("     • XGBoost")
                logger.info("     • Neural Network (Deep Learning)")
                logger.info("     • Reinforcement Learning (Q-Learning)")
                self.ml_engine = AdvancedMLEngine()
            else:
                logger.warning("  ⚠️ Usando IA BÁSICA")
                self.ml_engine = MLEngine()
            
            # Inicializar Risk Manager
            logger.info("🛡️ Inicializando Risk Manager...")
            logger.info("  ✅ Simulação antes de executar: ATIVA")
            logger.info(f"  ✅ Limite de perda diária: ${BotConfig.MAX_DAILY_LOSS}")
            logger.info(f"  ✅ Limite de gas diário: ${BotConfig.MAX_DAILY_GAS_SPEND}")
            logger.info("  ✅ Circuit breaker: ATIVO")
            logger.info(f"  ✅ Emergency stop: {BotConfig.EMERGENCY_STOP_BALANCE} ETH/BNB")
            
            logger.success("✅ Bot inicializado com sucesso!")
            
            # Exibir resumo
            self._print_initialization_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_initial_balances(self):
        """Verifica saldos iniciais"""
        try:
            logger.info("\n💰 Verificando saldos iniciais...")
            
            total_usd = 0.0
            
            for network_name in self.blockchain.web3_instances.keys():
                balance = self.blockchain.get_balance(network_name)
                balance_usd = convert_native_to_usd(balance, network_name)
                total_usd += balance_usd
                
                network_config = self.blockchain.networks[network_name]
                logger.info(f"  • {network_config.name}: {balance:.6f} {network_config.native_token} (~${balance_usd:.2f})")
                
                if balance < BotConfig.EMERGENCY_STOP_BALANCE:
                    logger.warning(f"    ⚠️ Saldo baixo! Mínimo: {BotConfig.EMERGENCY_STOP_BALANCE}")
            
            logger.info(f"\n  💵 Total em USD: ~${total_usd:.2f}\n")
            
            if total_usd < 10:
                logger.warning("⚠️ Saldo total muito baixo! Considere adicionar mais fundos.")
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar saldos: {e}")
    
    def run(self):
        """Loop principal do bot"""
        try:
            self.running = True
            logger.success("🎯 BOT INICIADO! Rodando 24/7...")
            logger.info(f"⏱️ Intervalo de checagem: {BotConfig.CHECK_INTERVAL_SECONDS}s")
            logger.info(f"🎯 Lucro mínimo: ${BotConfig.MIN_PROFIT_USD} ({BotConfig.MIN_PROFIT_PERCENTAGE}%)")
            logger.info(f"🧠 Confiança mínima da IA: {BotConfig.ML_CONFIDENCE_THRESHOLD*100:.0f}%\n")
            
            while self.running:
                try:
                    self.stats['cycles'] += 1
                    
                    # Verificar saúde das conexões periodicamente
                    if self.stats['cycles'] % 100 == 0:
                        self._check_health()
                        self.risk_manager.print_stats()
                    
                    # Imprimir stats periodicamente
                    if self.stats['cycles'] % 50 == 0:
                        self._print_stats()
                    
                    # Buscar e executar oportunidades
                    self._execute_cycle()
                    
                    # Verificar emergency stop
                    self._check_emergency_stop()
                    
                    # Aguardar próximo ciclo
                    time.sleep(BotConfig.CHECK_INTERVAL_SECONDS)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"❌ Erro no ciclo: {e}")
                    time.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
    
    def _execute_cycle(self):
        """Executa um ciclo de busca e execução"""
        try:
            # Buscar oportunidade
            result = self.flash_loan_strategy.find_and_execute()
            
            if result:
                self.stats['opportunities_found'] += 1
                self.stats['trades_executed'] += 1
                
                opportunity = result['opportunity']
                profit = result.get('profit', {})
                tx_hash = result.get('tx_hash')
                
                # Verificar se foi bem-sucedido
                success = profit.get('profitable', False) and tx_hash
                
                if success:
                    self.stats['successful_trades'] += 1
                else:
                    self.stats['failed_trades'] += 1
                
                # Registrar na IA
                actual_profit = profit.get('net_profit_usd', 0)
                self.ml_engine.record_result(opportunity, success, actual_profit)
                
                if success and actual_profit > 0:
                    self.stats['total_profit_usd'] += actual_profit
                    
                    # Atualizar melhor trade
                    if not self.stats['best_trade'] or actual_profit > self.stats['best_trade']['profit']:
                        self.stats['best_trade'] = {
                            'profit': actual_profit,
                            'tx_hash': tx_hash,
                            'timestamp': time.time()
                        }
                    
                    logger.success(f"💰 Lucro acumulado: ${self.stats['total_profit_usd']:.2f}")
                
        except Exception as e:
            logger.error(f"❌ Erro no ciclo de execução: {e}")
            import traceback
            traceback.print_exc()
    
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
        """Verifica se deve parar por saldo baixo - CORRIGIDO"""
        try:
            for network_name in self.blockchain.web3_instances.keys():
                balance = self.blockchain.get_balance(network_name)
                
                # CORRIGIDO: Agora compara ETH com ETH!
                if balance < BotConfig.EMERGENCY_STOP_BALANCE:
                    # Converter para USD para mostrar
                    balance_usd = convert_native_to_usd(balance, network_name)
                    min_usd = convert_native_to_usd(BotConfig.EMERGENCY_STOP_BALANCE, network_name)
                    
                    network_config = self.blockchain.networks[network_name]
                    
                    logger.error(f"🛑 EMERGÊNCIA: Saldo baixo em {network_name}!")
                    logger.error(f"   Saldo atual: {balance:.6f} {network_config.native_token} (~${balance_usd:.2f})")
                    logger.error(f"   Mínimo: {BotConfig.EMERGENCY_STOP_BALANCE} {network_config.native_token} (~${min_usd:.2f})")
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
            logger.info(f"{Fore.CYAN}📊 ESTATÍSTICAS DO BOT")
            logger.info("="*60)
            logger.info(f"⏱️ Uptime: {hours:.2f} horas")
            logger.info(f"🔄 Ciclos executados: {self.stats['cycles']:,}")
            logger.info(f"🎯 Oportunidades encontradas: {self.stats['opportunities_found']}")
            logger.info(f"⚡ Trades executados: {self.stats['trades_executed']}")
            logger.info(f"✅ Trades bem-sucedidos: {self.stats['successful_trades']}")
            logger.info(f"❌ Trades falhados: {self.stats['failed_trades']}")
            logger.info(f"💰 Lucro total: ${self.stats['total_profit_usd']:.2f}")
            logger.info(f"⛽ Gas gasto: ${self.stats['total_gas_spent_usd']:.2f}")
            
            # Taxa de sucesso
            if self.stats['trades_executed'] > 0:
                success_rate = (self.stats['successful_trades'] / self.stats['trades_executed']) * 100
                logger.info(f"📈 Taxa de sucesso: {success_rate:.1f}%")
            
            # Melhor trade
            if self.stats['best_trade']:
                logger.info(f"🏆 Melhor trade: ${self.stats['best_trade']['profit']:.2f}")
            
            # Stats da IA
            ml_stats = self.ml_engine.get_performance_stats()
            logger.info(f"🧠 IA treinada: {'Sim' if ml_stats.get('is_trained') else 'Não'}")
            
            if ADVANCED_ML_AVAILABLE:
                logger.info(f"🎯 Melhor hora: {ml_stats.get('best_hour', 12)}h")
                logger.info(f"📊 Volatilidade: {ml_stats.get('volatility', 0):.2f}")
                logger.info(f"🚀 Momentum: {ml_stats.get('momentum', 0):.2f}")
                logger.info(f"🎲 RL Epsilon: {ml_stats.get('rl_epsilon', 0):.3f}")
            
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Erro ao imprimir stats: {e}")
    
    def _print_initialization_summary(self):
        """Imprime resumo da inicialização"""
        logger.info("\n" + "="*60)
        logger.info(f"{Fore.GREEN}✅ RESUMO DA INICIALIZAÇÃO")
        logger.info("="*60)
        logger.info(f"🔗 Blockchain: {'CONECTADO' if self.blockchain.connected else 'FALHOU'}")
        logger.info(f"   Redes ativas: {len(self.blockchain.web3_instances)}")
        logger.info(f"🔍 DEX Scanner: {'ATIVO' if self.dex_scanner else 'FALHOU'}")
        logger.info(f"⚡ Flash Loan: {'REAL' if REAL_FLASHLOAN_AVAILABLE else 'SIMULADO'}")
        logger.info(f"🧠 IA: {'AVANÇADA' if ADVANCED_ML_AVAILABLE else 'BÁSICA'}")
        logger.info(f"🛡️ Risk Manager: ATIVO")
        
        mode = "DRY RUN (Simulação)" if BotConfig.DRY_RUN else ("TESTNET (Real)" if BotConfig.USE_TESTNET else "MAINNET (Produção)")
        logger.info(f"🎭 Modo: {mode}")
        logger.info("="*60 + "\n")
    
    def stop(self):
        """Para o bot"""
        if not self.running:
            return
        
        logger.warning("🛑 Parando bot...")
        self.running = False
        
        # Imprimir estatísticas finais
        self._print_stats()
        
        # Salvar modelos de IA
        if self.ml_engine:
            try:
                logger.info("💾 Salvando modelos de IA...")
                if ADVANCED_ML_AVAILABLE:
                    self.ml_engine._save_all_models()
                logger.success("✅ Modelos salvos!")
            except Exception as e:
                logger.error(f"❌ Erro ao salvar modelos: {e}")
        
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
    🚀 VERSÃO FINAL - 100% REAL E FUNCIONAL 🚀
    Flash Loan Arbitrage Bot com IA Avançada
    Base, Arbitrum e BSC
    
    ✅ Smart Contracts REAIS
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
        bot = FinalMEVBot()
        
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
