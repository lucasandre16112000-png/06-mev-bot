"""
🛡️ GERENCIADOR DE RISCO
Sistema completo de proteção contra prejuízo
"""

import time
from typing import Dict, Optional, Tuple
from loguru import logger
from datetime import datetime, timedelta
import json
import os

from src.config.config import BotConfig

class RiskManager:
    """Gerenciador de risco e proteção contra prejuízo"""
    
    def __init__(self):
        self.daily_stats = {
            'date': datetime.now().date(),
            'gas_spent': 0.0,
            'profit': 0.0,
            'loss': 0.0,
            'trades_executed': 0,
            'trades_failed': 0,
            'consecutive_failures': 0
        }
        
        self.total_stats = {
            'total_gas_spent': 0.0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'total_trades': 0,
            'start_time': time.time()
        }
        
        self.circuit_breaker_active = False
        self.emergency_stop = False
        self.max_consecutive_failures = BotConfig.MAX_CONSECUTIVE_FAILURES
        
        # Carregar stats anteriores se existirem
        self._load_stats()
    
    @property
    def consecutive_failures(self) -> int:
        """Retorna número de falhas consecutivas"""
        return self.daily_stats.get('consecutive_failures', 0)
    
    def _load_stats(self):
        """Carrega estatísticas salvas"""
        try:
            stats_file = "data/risk_stats.json"
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    self.total_stats.update(data.get('total_stats', {}))
                    logger.info("📊 Estatísticas anteriores carregadas")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar stats: {e}")
    
    def _save_stats(self):
        """Salva estatísticas"""
        try:
            os.makedirs("data", exist_ok=True)
            stats_file = "data/risk_stats.json"
            
            data = {
                'daily_stats': {
                    **self.daily_stats,
                    'date': str(self.daily_stats['date'])
                },
                'total_stats': self.total_stats
            }
            
            with open(stats_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar stats: {e}")
    
    def _reset_daily_stats(self):
        """Reseta estatísticas diárias"""
        today = datetime.now().date()
        
        if self.daily_stats['date'] != today:
            logger.info("📅 Novo dia! Resetando estatísticas diárias...")
            self.daily_stats = {
                'date': today,
                'gas_spent': 0.0,
                'profit': 0.0,
                'loss': 0.0,
                'trades_executed': 0,
                'trades_failed': 0,
                'consecutive_failures': 0
            }
            
            # Resetar circuit breaker
            if self.circuit_breaker_active:
                logger.info("🔓 Circuit breaker resetado")
                self.circuit_breaker_active = False
    
    def can_execute_trade(self, estimated_gas_cost: float) -> Tuple[bool, str]:
        """
        Verifica se pode executar um trade
        
        Returns:
            (pode_executar, motivo)
        """
        self._reset_daily_stats()
        
        # 1. Verificar emergency stop
        if self.emergency_stop:
            return False, "🛑 EMERGENCY STOP ativado!"
        
        # 2. Verificar circuit breaker
        if self.circuit_breaker_active:
            return False, "⚠️ Circuit breaker ativado (muitas falhas consecutivas)"
        
        # 3. Verificar limite de gas diário
        if self.daily_stats['gas_spent'] + estimated_gas_cost > BotConfig.MAX_DAILY_GAS_SPEND:
            remaining = BotConfig.MAX_DAILY_GAS_SPEND - self.daily_stats['gas_spent']
            return False, f"⛽ Limite de gas diário atingido (restante: ${remaining:.2f})"
        
        # 4. Verificar limite de perdas diárias
        daily_pnl = self.daily_stats['profit'] - self.daily_stats['loss'] - self.daily_stats['gas_spent']
        
        if daily_pnl < -BotConfig.MAX_DAILY_LOSS:
            return False, f"📉 Limite de perda diária atingido (perda: ${abs(daily_pnl):.2f})"
        
        # 5. Verificar falhas consecutivas
        if self.daily_stats['consecutive_failures'] >= BotConfig.MAX_CONSECUTIVE_FAILURES:
            self.circuit_breaker_active = True
            return False, f"🔴 Circuit breaker ativado! ({self.daily_stats['consecutive_failures']} falhas consecutivas)"
        
        return True, "✅ Pode executar"
    
    def simulate_transaction(self, blockchain, network: str, transaction: dict) -> Tuple[bool, Optional[str]]:
        """
        Simula uma transação ANTES de executar
        
        Returns:
            (sucesso, erro_msg)
        """
        try:
            w3 = blockchain.get_web3(network)
            if not w3:
                return False, "Rede não disponível"
            
            logger.info("🎬 Simulando transação...")
            
            # Tentar estimar gas
            try:
                gas_estimate = w3.eth.estimate_gas(transaction)
                logger.info(f"  ⛽ Gas estimado: {gas_estimate:,}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"  ❌ Simulação falhou: {error_msg}")
                
                # Analisar erro
                if "insufficient funds" in error_msg.lower():
                    return False, "Saldo insuficiente"
                elif "revert" in error_msg.lower():
                    return False, "Transação seria revertida (não lucrativa)"
                elif "gas required exceeds allowance" in error_msg.lower():
                    return False, "Gas muito alto"
                else:
                    return False, f"Erro na simulação: {error_msg[:100]}"
            
            logger.success("  ✅ Simulação bem-sucedida!")
            return True, None
            
        except Exception as e:
            logger.error(f"❌ Erro ao simular: {e}")
            return False, str(e)
    
    def check_slippage(self, expected_output: float, actual_output: float, max_slippage: float = 0.02) -> bool:
        """
        Verifica slippage (variação de preço)
        
        Args:
            expected_output: Valor esperado
            actual_output: Valor real
            max_slippage: Slippage máximo permitido (2% padrão)
        
        Returns:
            True se slippage está OK, False se excedeu
        """
        if expected_output == 0:
            return False
        
        slippage = abs(actual_output - expected_output) / expected_output
        
        if slippage > max_slippage:
            logger.warning(f"⚠️ Slippage muito alto: {slippage*100:.2f}% (máx: {max_slippage*100:.2f}%)")
            return False
        
        logger.info(f"✅ Slippage OK: {slippage*100:.2f}%")
        return True
    
    def record_trade_result(self, success: bool, profit: float, gas_cost: float):
        """Registra resultado de um trade"""
        self._reset_daily_stats()
        
        # Atualizar stats diárias
        self.daily_stats['gas_spent'] += gas_cost
        
        if success:
            self.daily_stats['profit'] += profit
            self.daily_stats['trades_executed'] += 1
            self.daily_stats['consecutive_failures'] = 0  # Resetar contador
            logger.success(f"✅ Trade bem-sucedido! Lucro: ${profit:.2f}")
        else:
            self.daily_stats['loss'] += abs(profit)  # profit negativo = loss
            self.daily_stats['trades_failed'] += 1
            self.daily_stats['consecutive_failures'] += 1
            logger.warning(f"❌ Trade falhou! Perda: ${abs(profit):.2f}")
        
        # Atualizar stats totais
        self.total_stats['total_gas_spent'] += gas_cost
        if success:
            self.total_stats['total_profit'] += profit
        else:
            self.total_stats['total_loss'] += abs(profit)
        self.total_stats['total_trades'] += 1
        
        # Salvar stats
        self._save_stats()
        
        # Verificar se deve ativar emergency stop
        self._check_emergency_conditions()
    
    def _check_emergency_conditions(self):
        """Verifica se deve ativar emergency stop"""
        # Calcular PnL total
        total_pnl = (
            self.total_stats['total_profit'] - 
            self.total_stats['total_loss'] - 
            self.total_stats['total_gas_spent']
        )
        
        # Se perdeu mais de 80% do capital inicial
        if total_pnl < -40:  # Assumindo $50 inicial
            logger.error("🛑 EMERGENCY STOP: Perda crítica detectada!")
            logger.error(f"   PnL total: ${total_pnl:.2f}")
            self.emergency_stop = True
    
    def get_daily_pnl(self) -> float:
        """Retorna lucro/prejuízo do dia"""
        return (
            self.daily_stats['profit'] - 
            self.daily_stats['loss'] - 
            self.daily_stats['gas_spent']
        )
    
    def get_total_pnl(self) -> float:
        """Retorna lucro/prejuízo total"""
        return (
            self.total_stats['total_profit'] - 
            self.total_stats['total_loss'] - 
            self.total_stats['total_gas_spent']
        )
    
    def get_stats_summary(self) -> Dict:
        """Retorna resumo de estatísticas"""
        return {
            'daily': {
                **self.daily_stats,
                'pnl': self.get_daily_pnl(),
                'date': str(self.daily_stats['date'])
            },
            'total': {
                **self.total_stats,
                'pnl': self.get_total_pnl(),
                'uptime_hours': (time.time() - self.total_stats['start_time']) / 3600
            },
            'status': {
                'circuit_breaker': self.circuit_breaker_active,
                'emergency_stop': self.emergency_stop
            }
        }
    
    def print_stats(self):
        """Imprime estatísticas formatadas"""
        daily_pnl = self.get_daily_pnl()
        total_pnl = self.get_total_pnl()
        
        logger.info("\n" + "="*60)
        logger.info("📊 ESTATÍSTICAS DE RISCO")
        logger.info("="*60)
        
        logger.info(f"📅 HOJE ({self.daily_stats['date']}):")
        logger.info(f"  💰 Lucro: ${self.daily_stats['profit']:.2f}")
        logger.info(f"  📉 Perda: ${self.daily_stats['loss']:.2f}")
        logger.info(f"  ⛽ Gas: ${self.daily_stats['gas_spent']:.2f}")
        logger.info(f"  📊 PnL: ${daily_pnl:.2f}")
        logger.info(f"  ✅ Trades OK: {self.daily_stats['trades_executed']}")
        logger.info(f"  ❌ Trades falhos: {self.daily_stats['trades_failed']}")
        
        logger.info(f"\n📈 TOTAL:")
        logger.info(f"  💰 Lucro total: ${self.total_stats['total_profit']:.2f}")
        logger.info(f"  📉 Perda total: ${self.total_stats['total_loss']:.2f}")
        logger.info(f"  ⛽ Gas total: ${self.total_stats['total_gas_spent']:.2f}")
        logger.info(f"  📊 PnL total: ${total_pnl:.2f}")
        logger.info(f"  🔢 Total trades: {self.total_stats['total_trades']}")
        
        logger.info(f"\n🛡️ PROTEÇÕES:")
        logger.info(f"  Circuit breaker: {'🔴 ATIVO' if self.circuit_breaker_active else '🟢 OK'}")
        logger.info(f"  Emergency stop: {'🛑 ATIVO' if self.emergency_stop else '🟢 OK'}")
        logger.info(f"  Falhas consecutivas: {self.daily_stats['consecutive_failures']}/{BotConfig.MAX_CONSECUTIVE_FAILURES}")
        
        logger.info("="*60 + "\n")
    
    def reset_circuit_breaker(self):
        """Reseta circuit breaker manualmente"""
        self.circuit_breaker_active = False
        self.daily_stats['consecutive_failures'] = 0
        logger.info("🔓 Circuit breaker resetado manualmente")
    
    def reset_emergency_stop(self):
        """Reseta emergency stop manualmente (use com cuidado!)"""
        self.emergency_stop = False
        logger.warning("⚠️ Emergency stop resetado manualmente!")
