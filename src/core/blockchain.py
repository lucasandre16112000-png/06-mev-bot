"""
🔗 MÓDULO DE CONEXÃO BLOCKCHAIN
Gerencia conexões Web3 com Base, Arbitrum e BSC
"""

import asyncio
from typing import Dict, Optional
from web3 import Web3, AsyncWeb3
# Middleware POA não é mais necessário na versão mais recente do web3.py
from eth_account import Account
from loguru import logger
import time

from src.config.config import (
    NETWORKS_MAINNET,
    NETWORKS_TESTNET,
    BotConfig
)

class BlockchainConnector:
    """Gerenciador de conexões blockchain"""
    
    def __init__(self):
        self.networks = NETWORKS_TESTNET if BotConfig.USE_TESTNET else NETWORKS_MAINNET
        self.web3_instances: Dict[str, Web3] = {}
        self.account: Optional[Account] = None
        self.connected = False
        
    def initialize(self) -> bool:
        """Inicializa todas as conexões"""
        try:
            logger.info("🔗 Inicializando conexões blockchain...")
            
            # Carregar conta
            if not self._load_account():
                return False
            
            # Conectar em todas as redes
            for network_name, network_config in self.networks.items():
                if not self._connect_network(network_name, network_config):
                    logger.warning(f"⚠️ Falha ao conectar em {network_name}")
                    continue
                    
            if not self.web3_instances:
                logger.error("❌ Nenhuma rede conectada!")
                return False
                
            self.connected = True
            logger.success(f"✅ Conectado em {len(self.web3_instances)} redes!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar: {e}")
            return False
    
    def _load_account(self) -> bool:
        """Carrega conta da private key"""
        try:
            if not BotConfig.PRIVATE_KEY:
                logger.error("❌ PRIVATE_KEY não configurada!")
                return False
                
            self.account = Account.from_key(BotConfig.PRIVATE_KEY)
            logger.info(f"✅ Conta carregada: {self.account.address}")
            
            # Validar endereço
            if BotConfig.WALLET_ADDRESS:
                if self.account.address.lower() != BotConfig.WALLET_ADDRESS.lower():
                    logger.warning("⚠️ Endereço da carteira não corresponde à private key!")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar conta: {e}")
            return False
    
    def _connect_network(self, name: str, config) -> bool:
        """Conecta em uma rede específica"""
        try:
            logger.info(f"🔌 Conectando em {config.name}...")
            
            # Criar instância Web3
            w3 = Web3(Web3.HTTPProvider(
                config.rpc_url,
                request_kwargs={'timeout': 60}
            ))
            
            # Middleware POA não é mais necessário na versão recente do web3.py
            # BSC funciona sem middleware adicional
            
            # Testar conexão
            if not w3.is_connected():
                logger.error(f"❌ Não foi possível conectar em {config.name}")
                return False
            
            # Verificar chain ID
            chain_id = w3.eth.chain_id
            if chain_id != config.chain_id:
                logger.warning(f"⚠️ Chain ID diferente: esperado {config.chain_id}, obtido {chain_id}")
            
            # Obter block number
            block_number = w3.eth.block_number
            logger.info(f"  📦 Último bloco: {block_number:,}")
            
            # Verificar saldo
            if self.account:
                balance_wei = w3.eth.get_balance(self.account.address)
                balance = w3.from_wei(balance_wei, 'ether')
                logger.info(f"  💰 Saldo: {balance:.6f} {config.native_token}")
                
                if balance == 0:
                    logger.warning(f"⚠️ Saldo zero em {config.name}!")
            
            self.web3_instances[name] = w3
            logger.success(f"✅ {config.name} conectado!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar em {name}: {e}")
            return False
    
    def get_web3(self, network: str) -> Optional[Web3]:
        """Retorna instância Web3 de uma rede"""
        return self.web3_instances.get(network)
    
    def get_balance(self, network: str, address: Optional[str] = None) -> float:
        """Retorna saldo em uma rede"""
        try:
            w3 = self.get_web3(network)
            if not w3:
                return 0.0
            
            addr = address or self.account.address
            balance_wei = w3.eth.get_balance(addr)
            return float(w3.from_wei(balance_wei, 'ether'))
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter saldo: {e}")
            return 0.0
    
    def get_gas_price(self, network: str) -> int:
        """Retorna gas price atual em wei"""
        try:
            w3 = self.get_web3(network)
            if not w3:
                return 0
            
            gas_price = w3.eth.gas_price
            return gas_price
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter gas price: {e}")
            return 0
    
    def estimate_gas(self, network: str, transaction: dict) -> int:
        """Estima gas necessário para uma transação"""
        try:
            w3 = self.get_web3(network)
            if not w3:
                return 0
            
            gas_estimate = w3.eth.estimate_gas(transaction)
            return gas_estimate
            
        except Exception as e:
            logger.error(f"❌ Erro ao estimar gas: {e}")
            return 0
    
    def send_transaction(self, network: str, transaction: dict) -> Optional[str]:
        """Envia uma transação"""
        try:
            w3 = self.get_web3(network)
            if not w3 or not self.account:
                return None
            
            # Adicionar nonce
            if 'nonce' not in transaction:
                transaction['nonce'] = w3.eth.get_transaction_count(self.account.address)
            
            # Adicionar gas price
            if 'gasPrice' not in transaction and 'maxFeePerGas' not in transaction:
                transaction['gasPrice'] = w3.eth.gas_price
            
            # Adicionar chain ID
            if 'chainId' not in transaction:
                transaction['chainId'] = w3.eth.chain_id
            
            # Assinar transação
            signed_txn = w3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Enviar transação
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"📤 Transação enviada: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar transação: {e}")
            return None
    
    def wait_for_transaction(self, network: str, tx_hash: str, timeout: int = 120) -> bool:
        """Aguarda confirmação de transação"""
        try:
            w3 = self.get_web3(network)
            if not w3:
                return False
            
            logger.info(f"⏳ Aguardando confirmação de {tx_hash[:10]}...")
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            
            if receipt.status == 1:
                logger.success(f"✅ Transação confirmada!")
                return True
            else:
                logger.error(f"❌ Transação falhou!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao aguardar transação: {e}")
            return False
    
    def get_transaction_receipt(self, network: str, tx_hash: str) -> Optional[dict]:
        """Retorna receipt de uma transação"""
        try:
            w3 = self.get_web3(network)
            if not w3:
                return None
            
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter receipt: {e}")
            return None
    
    def check_health(self) -> Dict[str, bool]:
        """Verifica saúde de todas as conexões"""
        health = {}
        
        for network_name, w3 in self.web3_instances.items():
            try:
                w3.eth.block_number
                health[network_name] = True
            except:
                health[network_name] = False
                logger.warning(f"⚠️ {network_name} não está respondendo!")
        
        return health
    
    def reconnect(self, network: str) -> bool:
        """Reconecta em uma rede específica"""
        logger.info(f"🔄 Reconectando em {network}...")
        
        if network in self.networks:
            return self._connect_network(network, self.networks[network])
        
        return False
    
    def close_all(self):
        """Fecha todas as conexões"""
        logger.info("🔌 Fechando todas as conexões...")
        self.web3_instances.clear()
        self.connected = False
    
    def get_connected_networks(self) -> list:
        """Retorna lista de redes conectadas"""
        return list(self.web3_instances.keys())
    
    def check_health(self) -> Dict[str, bool]:
        """Verifica saúde de todas as conexões"""
        health = {}
        
        for network_name, w3 in self.web3_instances.items():
            try:
                # Tentar obter último bloco
                w3.eth.block_number
                health[network_name] = True
            except:
                health[network_name] = False
        
        return health
    
    def reconnect(self, network: str) -> bool:
        """Reconecta uma rede específica"""
        try:
            if network not in self.networks:
                return False
            
            logger.info(f"🔄 Reconectando {network}...")
            return self._connect_network(network, self.networks[network])
            
        except Exception as e:
            logger.error(f"❌ Erro ao reconectar: {e}")
            return False

# Instância global
blockchain = BlockchainConnector()
