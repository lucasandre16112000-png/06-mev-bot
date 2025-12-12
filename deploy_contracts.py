"""
🚀 SCRIPT DE DEPLOYMENT DE CONTRATOS - VERSÃO CORRIGIDA
Deploy automático dos contratos FlashLoanArbitrage em todas as redes
"""

import os
import json
import time
from typing import Optional, Dict, List
from web3 import Web3
from eth_account import Account
from loguru import logger
from colorama import init, Fore, Style
from solcx import compile_standard, install_solc, set_solc_version
import sys

init(autoreset=True)

from src.config.config import (
    NETWORKS_MAINNET,
    NETWORKS_TESTNET,
    AAVE_V3_POOL,
    UNISWAP_V3_ROUTER,
    BotConfig
)

class ContractDeployer:
    """Deployer de contratos inteligentes"""
    
    def __init__(self):
        self.networks = NETWORKS_TESTNET if BotConfig.USE_TESTNET else NETWORKS_MAINNET
        self.account = None
        self.deployed_addresses = {}
        
    def load_account(self) -> bool:
        """Carrega conta da private key"""
        try:
            self.account = Account.from_key(BotConfig.PRIVATE_KEY)
            logger.info(f"✅ Conta carregada: {self.account.address}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao carregar conta: {e}")
            return False
    
    def compile_contract(self, contract_file: str) -> Optional[dict]:
        """Compila contrato Solidity usando Standard JSON com viaIR"""
        try:
            logger.info(f"📝 Compilando {contract_file}...")
            
            # Instalar versão correta do Solidity
            install_solc('0.8.20')
            set_solc_version('0.8.20')
            
            # Ler contrato principal
            with open(contract_file, 'r') as f:
                contract_source = f.read()
            
            # Ler todas as interfaces
            interfaces = {}
            interface_files = [
                'IERC20.sol',
                'IPool.sol',
                'IPoolAddressesProvider.sol',
                'ISwapRouter.sol'
            ]
            
            for iface_file in interface_files:
                iface_path = f'contracts/interfaces/{iface_file}'
                with open(iface_path, 'r') as f:
                    interfaces[f'interfaces/{iface_file}'] = {'content': f.read()}
            
            # Preparar input JSON padrão
            input_json = {
                'language': 'Solidity',
                'sources': {
                    'FlashLoanArbitrageV2.sol': {'content': contract_source},
                    **interfaces
                },
                'settings': {
                    'optimizer': {
                        'enabled': True,
                        'runs': 200
                    },
                    'viaIR': True,  # IMPORTANTE: Necessário para contratos complexos
                    'outputSelection': {
                        '*': {
                            '*': ['abi', 'evm.bytecode', 'evm.bytecode.object']
                        }
                    }
                }
            }
            
            # Compilar
            output = compile_standard(input_json, solc_version='0.8.20')
            
            # Extrair contrato principal
            contract_data = output['contracts']['FlashLoanArbitrageV2.sol']['FlashLoanArbitrageV2']
            
            contract_interface = {
                'abi': contract_data['abi'],
                'bin': contract_data['evm']['bytecode']['object']
            }
            
            logger.success(f"✅ Contrato compilado com sucesso!")
            return contract_interface
            
        except Exception as e:
            logger.error(f"❌ Erro na compilação: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def deploy_to_network(
        self,
        network_name: str,
        network_config,
        contract_interface: dict
    ) -> Optional[str]:
        """Deploy do contrato em uma rede específica"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🌐 Fazendo deploy em {network_config.name}...")
            logger.info(f"{'='*60}")
            
            # Conectar na rede
            w3 = Web3(Web3.HTTPProvider(network_config.rpc_url))
            
            if not w3.is_connected():
                logger.error(f"❌ Não foi possível conectar em {network_config.name}")
                return None
            
            logger.info(f"✅ Conectado em {network_config.name}")
            
            # Verificar saldo
            balance = w3.eth.get_balance(self.account.address)
            balance_eth = w3.from_wei(balance, 'ether')
            logger.info(f"💰 Saldo: {balance_eth:.4f} {network_config.native_token}")
            
            if balance == 0:
                logger.error(f"❌ Sem saldo para pagar gas!")
                return None
            
            # Pegar endereço do Aave Pool
            if network_name not in AAVE_V3_POOL:
                logger.warning(f"⚠️ Aave V3 não disponível em {network_name}")
                return None
            
            aave_pool = AAVE_V3_POOL[network_name]
            
            # Pegar endereço do Uniswap Router
            if network_name not in UNISWAP_V3_ROUTER:
                logger.warning(f"⚠️ Uniswap V3 não disponível em {network_name}")
                return None
            
            uniswap_router = UNISWAP_V3_ROUTER[network_name]
            
            # Criar contrato
            Contract = w3.eth.contract(
                abi=contract_interface['abi'],
                bytecode=contract_interface['bin']
            )
            
            # Construir transação de deployment
            logger.info("📝 Construindo transação de deployment...")
            
            constructor_args = [aave_pool, uniswap_router]  # Aave Pool + Uniswap Router
            
            transaction = Contract.constructor(*constructor_args).build_transaction({
                'from': self.account.address,
                'nonce': w3.eth.get_transaction_count(self.account.address),
                'gas': 5000000,  # Gas limit alto para deployment
                'gasPrice': w3.eth.gas_price,
            })
            
            # Assinar transação
            logger.info("✍️ Assinando transação...")
            signed_txn = w3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Enviar transação
            logger.info("📤 Enviando transação...")
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            logger.info(f"⏳ Aguardando confirmação... (tx: {tx_hash.hex()})")
            
            # Aguardar confirmação
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt['status'] == 1:
                contract_address = tx_receipt['contractAddress']
                logger.success(f"✅ Deploy bem-sucedido!")
                logger.success(f"📍 Endereço do contrato: {contract_address}")
                logger.info(f"⛽ Gas usado: {tx_receipt['gasUsed']}")
                
                return contract_address
            else:
                logger.error(f"❌ Deploy falhou! Status: {tx_receipt['status']}")
                logger.error(f"🔍 TX Hash: {tx_hash.hex()}")
                logger.error(f"⛽ Gas usado: {tx_receipt.get('gasUsed', 'N/A')}")
                
                # Tentar obter razão do revert
                try:
                    tx = w3.eth.get_transaction(tx_hash)
                    replay = w3.eth.call(tx, tx_receipt['blockNumber'])
                    logger.error(f"🐞 Replay: {replay}")
                except Exception as replay_err:
                    logger.error(f"⚠️ Não foi possível obter razão do revert: {replay_err}")
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no deployment: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def deploy_all(self):
        """Deploy em todas as redes configuradas"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🚀 DEPLOYMENT DE CONTRATOS MEV BOT")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Carregar conta
        if not self.load_account():
            return False
        
        # Compilar contrato
        contract_interface = self.compile_contract('contracts/FlashLoanArbitrageV2.sol')
        
        if not contract_interface:
            logger.error("❌ Falha na compilação!")
            return False
        
        # Deploy em cada rede
        for network_name, network_config in self.networks.items():
            if not network_config.enabled:
                logger.info(f"⏭️ Pulando {network_name} (desabilitado)")
                continue
            
            contract_address = self.deploy_to_network(
                network_name,
                network_config,
                contract_interface
            )
            
            if contract_address:
                self.deployed_addresses[network_name] = {
                    'FlashLoanArbitrageV2': contract_address,
                    'deployed': True,
                    'timestamp': time.time()
                }
            else:
                self.deployed_addresses[network_name] = {
                    'FlashLoanArbitrageV2': '0x0000000000000000000000000000000000000000',
                    'deployed': False,
                    'error': 'Deployment failed'
                }
            
            # Aguardar entre deployments
            time.sleep(2)
        
        # Salvar endereços
        self.save_addresses()
        
        # Resumo
        self.print_summary()
        
        return True
    
    def save_addresses(self):
        """Salva endereços dos contratos deployados"""
        os.makedirs('data', exist_ok=True)
        
        with open('data/deployed_contracts.json', 'w') as f:
            json.dump(self.deployed_addresses, f, indent=2)
        
        logger.success("✅ Endereços salvos em data/deployed_contracts.json")
    
    def print_summary(self):
        """Imprime resumo do deployment"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}📊 RESUMO DO DEPLOYMENT")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        success_count = sum(1 for addr in self.deployed_addresses.values() if addr.get('deployed', False))
        total_count = len(self.deployed_addresses)
        
        for network, data in self.deployed_addresses.items():
            if data.get('deployed'):
                print(f"{Fore.GREEN}✅ {network}: {data['FlashLoanArbitrageV2']}")
            else:
                print(f"{Fore.RED}❌ {network}: Falhou")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        if success_count == total_count and total_count > 0:
            print(f"{Fore.GREEN}✅ DEPLOYMENT CONCLUÍDO COM SUCESSO!")
        elif success_count > 0:
            print(f"{Fore.YELLOW}⚠️ DEPLOYMENT PARCIAL: {success_count}/{total_count}")
        else:
            print(f"{Fore.RED}❌ DEPLOYMENT FALHOU!")
        print(f"{Fore.CYAN}{'='*60}\n")

if __name__ == "__main__":
    deployer = ContractDeployer()
    success = deployer.deploy_all()
    sys.exit(0 if success else 1)
