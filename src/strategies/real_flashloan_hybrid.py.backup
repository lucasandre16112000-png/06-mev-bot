"""
⚡ MÓDULO DE FLASH LOAN HÍBRIDO
Execução REAL com suporte híbrido para diferentes redes
VERSÃO MELHORADA - Funciona em TODAS as redes
"""

from typing import Dict, Optional, List
from web3 import Web3
from web3.contract import Contract
from loguru import logger
import json
import time
from eth_account import Account

from src.config.config import AAVE_V3_POOL, BotConfig

# ABI do contrato FlashLoanArbitrageHybrid
FLASH_LOAN_HYBRID_ABI = json.loads('''[
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "address", "name": "buyDex", "type": "address"},
            {"internalType": "address", "name": "sellDex", "type": "address"},
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "address", "name": "tokenOut", "type": "address"},
            {"internalType": "uint256", "name": "minProfit", "type": "uint256"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "executeArbitrage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getStats",
        "outputs": [
            {"internalType": "uint256", "name": "_totalArbitrages", "type": "uint256"},
            {"internalType": "uint256", "name": "_successfulArbitrages", "type": "uint256"},
            {"internalType": "uint256", "name": "_failedArbitrages", "type": "uint256"},
            {"internalType": "uint256", "name": "_totalProfit", "type": "uint256"},
            {"internalType": "uint256", "name": "_totalGasSpent", "type": "uint256"},
            {"internalType": "uint256", "name": "_averageProfit", "type": "uint256"},
            {"internalType": "uint256", "name": "_lastExecutionTime", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getMode",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"}],
        "name": "getBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "withdrawProfit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bool", "name": "_paused", "type": "bool"}],
        "name": "setPaused",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]''')


class HybridFlashLoanExecutor:
    """Executor HÍBRIDO de Flash Loans - Funciona em todas as redes"""
    
    def __init__(self, blockchain_connector):
        self.blockchain = blockchain_connector
        self.contracts = {}
        self.contract_addresses = {}
        
        # Carregar endereços dos contratos deployados
        self._load_contract_addresses()
        
        # Inicializar contratos
        self._initialize_contracts()
    
    def _load_contract_addresses(self):
        """Carrega endereços dos contratos deployados"""
        try:
            import os
            addresses_file = "data/deployed_contracts.json"
            
            if os.path.exists(addresses_file):
                with open(addresses_file, 'r') as f:
                    self.contract_addresses = json.load(f)
                logger.info("✅ Endereços de contratos híbridos carregados")
            else:
                logger.warning("⚠️ Arquivo de contratos não encontrado. Execute deploy_contracts_hybrid.py!")
                self.contract_addresses = {}
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar endereços: {e}")
            self.contract_addresses = {}
    
    def _initialize_contracts(self):
        """Inicializa instâncias dos contratos híbridos"""
        try:
            for network_name, w3 in self.blockchain.web3_instances.items():
                if network_name in self.contract_addresses:
                    contract_data = self.contract_addresses[network_name]
                    
                    if isinstance(contract_data, dict):
                        # Verificar se foi deployado com sucesso
                        if not contract_data.get('success', False):
                            logger.warning(f"⚠️ Contrato não deployado em {network_name}")
                            continue
                        
                        # Buscar endereço do contrato híbrido
                        contract_address = contract_data.get('address', '')
                        if not contract_address or contract_address == '0x0000000000000000000000000000000000000000':
                            logger.warning(f"⚠️ Endereço inválido em {network_name}")
                            continue
                    else:
                        contract_address = contract_data
                    
                    contract = w3.eth.contract(
                        address=Web3.to_checksum_address(contract_address),
                        abi=FLASH_LOAN_HYBRID_ABI
                    )
                    
                    # Verificar modo do contrato
                    try:
                        mode = contract.functions.getMode().call()
                        logger.info(f"✅ Contrato híbrido em {network_name}: {mode}")
                    except:
                        mode = "Unknown"
                    
                    self.contracts[network_name] = {
                        'address': contract_address,
                        'contract': contract,
                        'mode': mode
                    }
                    
                    logger.info(f"✅ Contrato inicializado em {network_name}: {contract_address[:10]}...")
                else:
                    logger.warning(f"⚠️ Contrato não deployado em {network_name}")
        
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar contratos: {e}")
    
    def calculate_flash_loan_fee(self, amount: int) -> int:
        """Calcula taxa de flash loan (0.09%)"""
        return int(amount * BotConfig.FLASH_LOAN_FEE)
    
    def estimate_profit(self, opportunity: Dict) -> Dict:
        """Estima lucro líquido REAL considerando todas as taxas"""
        try:
            network = opportunity['network']
            w3 = self.blockchain.get_web3(network)
            
            if not w3:
                return {'profitable': False, 'reason': 'Network unavailable'}
            
            amount_in = opportunity['amount_in']
            amount_out = opportunity.get('amount_out_sell', 0)
            
            # Taxa de flash loan
            flash_loan_fee = self.calculate_flash_loan_fee(amount_in)
            
            # Estimar gas REAL
            gas_estimate = self._estimate_gas_cost(network, opportunity)
            
            # Lucro bruto
            gross_profit = amount_out - amount_in
            
            # Lucro líquido
            net_profit = gross_profit - flash_loan_fee - gas_estimate
            
            # Converter para USD (simplificado - em produção usar oracle)
            net_profit_usd = float(w3.from_wei(net_profit, 'mwei')) if net_profit > 0 else 0
            
            return {
                'gross_profit': gross_profit,
                'flash_loan_fee': flash_loan_fee,
                'gas_cost': gas_estimate,
                'net_profit': net_profit,
                'net_profit_usd': net_profit_usd,
                'profitable': net_profit > 0,
                'roi': (net_profit / amount_in * 100) if amount_in > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao estimar lucro: {e}")
            return {'profitable': False, 'reason': str(e)}
    
    def _estimate_gas_cost(self, network: str, opportunity: Dict) -> int:
        """Estima custo de gas REAL"""
        try:
            w3 = self.blockchain.get_web3(network)
            if not w3:
                return 0
            
            # Gas price atual
            gas_price = w3.eth.gas_price
            
            # Estimativa de gas units (baseado em execuções anteriores)
            # Flash loan + 2 swaps = ~500k gas
            estimated_gas_units = 500000
            
            # Custo total em wei
            gas_cost_wei = gas_price * estimated_gas_units
            
            return gas_cost_wei
            
        except Exception as e:
            logger.error(f"❌ Erro ao estimar gas: {e}")
            return 0
    
    def execute_flash_loan_arbitrage(self, opportunity: Dict) -> Optional[str]:
        """
        Executa flash loan arbitrage HÍBRIDO na blockchain
        
        Esta versão funciona em TODAS as redes, inclusive Ethereum Sepolia
        """
        try:
            network = opportunity['network']
            
            # Verificar se contrato existe
            if network not in self.contracts:
                logger.error(f"❌ Contrato não disponível em {network}")
                logger.info(f"💡 Execute: python deploy_contracts_hybrid.py")
                return None
            
            contract_info = self.contracts[network]
            contract = contract_info['contract']
            w3 = self.blockchain.get_web3(network)
            
            # Estimar lucro
            profit_analysis = self.estimate_profit(opportunity)
            
            if not profit_analysis['profitable']:
                logger.warning(f"⚠️ Não lucrativo: {profit_analysis.get('reason', 'Unknown')}")
                return None
            
            logger.info(f"💰 Lucro estimado: ${profit_analysis['net_profit_usd']:.2f}")
            logger.info(f"📊 ROI estimado: {profit_analysis['roi']:.2f}%")
            logger.info(f"🎯 Modo: {contract_info.get('mode', 'Unknown')}")
            
            # Preparar parâmetros da transação
            asset = Web3.to_checksum_address(opportunity['token_in'])
            amount = opportunity['amount_in']
            
            # Endereços das DEXs (ou address(0) para modo Aave-only)
            buy_dex = Web3.to_checksum_address(
                opportunity.get('buy_dex_address', '0x0000000000000000000000000000000000000000')
            )
            sell_dex = Web3.to_checksum_address(
                opportunity.get('sell_dex_address', '0x0000000000000000000000000000000000000000')
            )
            
            token_in = Web3.to_checksum_address(opportunity['token_in'])
            token_out = Web3.to_checksum_address(opportunity['token_out'])
            min_profit = int(profit_analysis['net_profit'] * 0.95)  # 95% do estimado
            deadline = int(time.time()) + 300  # 5 minutos
            
            # Verificar se está em DRY RUN
            if BotConfig.DRY_RUN:
                logger.warning("🎭 MODO DRY RUN - Simulando execução...")
                return self._simulate_real_execution(opportunity, profit_analysis)
            
            # EXECUTAR TRANSAÇÃO REAL
            logger.info("🚀 Executando flash loan HÍBRIDO na blockchain...")
            
            # Construir transação
            tx = contract.functions.executeArbitrage(
                asset,
                amount,
                buy_dex,
                sell_dex,
                token_in,
                token_out,
                min_profit,
                deadline
            ).build_transaction({
                'from': self.blockchain.account.address,
                'nonce': w3.eth.get_transaction_count(self.blockchain.account.address),
                'gas': 800000,  # Limite de gas
                'gasPrice': w3.eth.gas_price,
                'chainId': w3.eth.chain_id
            })
            
            # Assinar transação
            signed_tx = w3.eth.account.sign_transaction(tx, self.blockchain.account.key)
            
            # Enviar transação
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.success(f"✅ Transação enviada: {tx_hash_hex}")
            logger.info("⏳ Aguardando confirmação...")
            
            # Aguardar confirmação
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                logger.success(f"🎉 FLASH LOAN EXECUTADO COM SUCESSO!")
                logger.info(f"  📝 TX: {tx_hash_hex}")
                logger.info(f"  ⛽ Gas usado: {receipt.gasUsed:,}")
                logger.info(f"  💰 Lucro estimado: ${profit_analysis['net_profit_usd']:.2f}")
                
                # Obter lucro real do contrato
                real_profit = self._get_actual_profit(network, receipt)
                if real_profit:
                    logger.success(f"  💵 Lucro REAL: ${real_profit:.2f}")
                
                return tx_hash_hex
            else:
                logger.error(f"❌ Transação FALHOU!")
                logger.error(f"  📝 TX: {tx_hash_hex}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar flash loan: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _simulate_real_execution(self, opportunity: Dict, profit_analysis: Dict) -> str:
        """Simula execução REAL (para DRY RUN)"""
        try:
            logger.info("🎬 SIMULANDO EXECUÇÃO HÍBRIDA...")
            logger.info(f"  📍 Rede: {opportunity['network']}")
            logger.info(f"  💱 Par: {opportunity.get('symbol_in', '?')} → {opportunity.get('symbol_out', '?')}")
            logger.info(f"  🏪 Compra em: {opportunity.get('buy_dex', 'N/A')}")
            logger.info(f"  🏪 Vende em: {opportunity.get('sell_dex', 'N/A')}")
            logger.info(f"  💵 Valor: ${opportunity['amount_in'] / 1e6:.2f}")
            logger.info(f"  💰 Lucro bruto: ${profit_analysis.get('gross_profit', 0) / 1e6:.2f}")
            logger.info(f"  💸 Taxa flash loan: ${profit_analysis.get('flash_loan_fee', 0) / 1e6:.2f}")
            logger.info(f"  ⛽ Gas estimado: ${profit_analysis.get('gas_cost', 0) / 1e18:.4f} ETH")
            logger.info(f"  💚 Lucro líquido: ${profit_analysis['net_profit_usd']:.2f}")
            logger.info(f"  📊 ROI: {profit_analysis['roi']:.2f}%")
            
            # Simular tempo de execução
            time.sleep(2)
            
            # Gerar hash simulado
            fake_tx_hash = f"0x{'1234567890abcdef' * 4}"
            
            logger.success(f"✅ Simulação concluída!")
            logger.info(f"  📝 TX Hash (simulado): {fake_tx_hash[:20]}...")
            logger.warning("  ⚠️ Para executar de verdade, mude DRY_RUN=false no .env")
            
            return fake_tx_hash
            
        except Exception as e:
            logger.error(f"❌ Erro na simulação: {e}")
            return None
    
    def _get_actual_profit(self, network: str, receipt) -> Optional[float]:
        """Obtém lucro real do contrato após execução"""
        try:
            # Analisar eventos do receipt para extrair lucro
            # Implementação simplificada
            return None
        except:
            return None
    
    def get_contract_stats(self, network: str) -> Optional[Dict]:
        """Obtém estatísticas do contrato"""
        try:
            if network not in self.contracts:
                return None
            
            contract = self.contracts[network]['contract']
            
            stats = contract.functions.getStats().call()
            
            return {
                'total_arbitrages': stats[0],
                'successful_arbitrages': stats[1],
                'failed_arbitrages': stats[2],
                'total_profit': stats[3],
                'total_gas_spent': stats[4],
                'average_profit': stats[5],
                'last_execution_time': stats[6],
                'success_rate': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats: {e}")
            return None


class HybridFlashLoanStrategy:
    """Estratégia completa de Flash Loan HÍBRIDO"""
    
    def __init__(self, blockchain_connector, dex_scanner):
        self.blockchain = blockchain_connector
        self.dex_scanner = dex_scanner
        self.executor = HybridFlashLoanExecutor(blockchain_connector)
        self.stats = {
            'opportunities_found': 0,
            'opportunities_executed': 0,
            'total_profit': 0.0,
            'success_rate': 0.0
        }
    
    def find_and_execute(self) -> Optional[Dict]:
        """Encontra e executa a melhor oportunidade HÍBRIDA"""
        try:
            # Buscar melhor oportunidade
            logger.info("🔍 Buscando oportunidades...")
            
            opportunity = self.dex_scanner.get_best_opportunity(
                min_profit_usd=BotConfig.MIN_PROFIT_USD,
                min_profit_pct=BotConfig.MIN_PROFIT_PERCENTAGE
            )
            
            if not opportunity:
                logger.debug("Nenhuma oportunidade encontrada")
                return None
            
            self.stats['opportunities_found'] += 1
            
            logger.success(f"🎯 Oportunidade encontrada!")
            logger.info(f"  💰 Lucro potencial: {opportunity['profit_percentage']:.2f}%")
            
            # Executar flash loan HÍBRIDO
            tx_hash = self.executor.execute_flash_loan_arbitrage(opportunity)
            
            if tx_hash:
                self.stats['opportunities_executed'] += 1
                
                # Atualizar estatísticas
                profit_analysis = self.executor.estimate_profit(opportunity)
                self.stats['total_profit'] += profit_analysis.get('net_profit_usd', 0)
                self.stats['success_rate'] = (
                    self.stats['opportunities_executed'] / self.stats['opportunities_found'] * 100
                )
                
                return {
                    'tx_hash': tx_hash,
                    'opportunity': opportunity,
                    'profit': profit_analysis,
                    'timestamp': time.time()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na estratégia: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da estratégia"""
        return self.stats.copy()
