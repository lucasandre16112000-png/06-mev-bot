"""
🚀 SCRIPT DE DEPLOYMENT DE CONTRATOS
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
from solcx import compile_source, install_solc, set_solc_version
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
        self.deployed_contracts = {}
        self.account = None
        
    def load_account(self) -> bool:
        """Carrega conta para deployment"""
        try:
            if not BotConfig.PRIVATE_KEY:
                logger.error("❌ PRIVATE_KEY não configurada!")
                return False
            
            self.account = Account.from_key(BotConfig.PRIVATE_KEY)
            logger.info(f"✅ Conta carregada: {self.account.address}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar conta: {e}")
            return False
    
    def compile_contract(self, contract_file: str) -> dict:
        """Compila contrato Solidity"""
        try:
            logger.info(f"📝 Compilando {contract_file}...")
            
            # Instalar versão correta do Solidity
            install_solc('0.8.20')
            set_solc_version('0.8.20')
            
            # Ler arquivo do contrato
            with open(contract_file, 'r') as f:
                contract_source = f.read()
            
            # Compilar com base_path para encontrar as interfaces
            import os
            base_path = os.path.dirname(os.path.abspath(contract_file))
            
            compiled = compile_source(
                contract_source,
                output_values=['abi', 'bin'],
                solc_version='0.8.20',
                base_path=base_path,
                allow_paths=[base_path]
            )
            
            # Pegar o contrato principal
            contract_id = list(compiled.keys())[0]
            contract_interface = compiled[contract_id]
            
            logger.success(f"✅ Contrato compilado!")
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
            logger.info(f"\n🚀 Deploying em {network_config.name}...")
            
            # Conectar na rede
            w3 = Web3(Web3.HTTPProvider(network_config.rpc_url))
            
            if not w3.is_connected():
                logger.error(f"❌ Não foi possível conectar em {network_config.name}")
                return None
            
            logger.info(f"  ✅ Conectado em {network_config.name}")
            
            # Verificar saldo
            balance = w3.eth.get_balance(self.account.address)
            balance_eth = w3.from_wei(balance, 'ether')
            logger.info(f"  💰 Saldo: {balance_eth:.6f} {network_config.native_token}")
            
            if balance == 0:
                logger.error(f"  ❌ Saldo zero! Adicione {network_config.native_token} para pagar gas")
                return None
            
            # Pegar endereços necessários
            aave_pool = AAVE_V3_POOL.get(network_name)
            uniswap_router = UNISWAP_V3_ROUTER.get(network_name)
            
            if not aave_pool or aave_pool == "0x0000000000000000000000000000000000000000":
                logger.warning(f"  ⚠️ Aave V3 não disponível em {network_name}")
                # Usar endereço placeholder
                aave_pool = "0x0000000000000000000000000000000000000001"
            
            if not uniswap_router:
                logger.warning(f"  ⚠️ Uniswap não disponível em {network_name}")
                uniswap_router = "0x0000000000000000000000000000000000000002"
            
            # Criar contrato
            Contract = w3.eth.contract(
                abi=contract_interface['abi'],
                bytecode=contract_interface['bin']
            )
            
            # Construir transação de deployment
            logger.info("  📝 Construindo transação de deployment...")
            
            constructor_tx = Contract.constructor(
                Web3.to_checksum_address(aave_pool),
                Web3.to_checksum_address(uniswap_router)
            ).build_transaction({
                'from': self.account.address,
                'nonce': w3.eth.get_transaction_count(self.account.address),
                'gas': 3000000,
                'gasPrice': w3.eth.gas_price,
                'chainId': network_config.chain_id
            })
            
            # Estimar gas
            try:
                gas_estimate = w3.eth.estimate_gas(constructor_tx)
                constructor_tx['gas'] = int(gas_estimate * 1.2)  # 20% buffer
                logger.info(f"  ⛽ Gas estimado: {gas_estimate:,}")
            except Exception as e:
                logger.warning(f"  ⚠️ Não foi possível estimar gas: {e}")
            
            # Calcular custo
            gas_cost = constructor_tx['gas'] * constructor_tx['gasPrice']
            gas_cost_eth = w3.from_wei(gas_cost, 'ether')
            logger.info(f"  💸 Custo estimado: {gas_cost_eth:.6f} {network_config.native_token}")
            
            # Confirmar
            if not BotConfig.DRY_RUN:
                confirm = input(f"\n  ❓ Confirma deployment em {network_config.name}? (sim/não): ")
                if confirm.lower() not in ['sim', 's', 'yes', 'y']:
                    logger.warning("  ⚠️ Deployment cancelado pelo usuário")
                    return None
            
            # Assinar transação
            logger.info("  ✍️ Assinando transação...")
            signed_tx = w3.eth.account.sign_transaction(constructor_tx, self.account.key)
            
            # Enviar transação
            logger.info("  📤 Enviando transação...")
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"  📝 TX Hash: {tx_hash_hex}")
            logger.info("  ⏳ Aguardando confirmação...")
            
            # Aguardar confirmação
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status == 1:
                contract_address = receipt.contractAddress
                logger.success(f"  🎉 CONTRATO DEPLOYADO COM SUCESSO!")
                logger.success(f"  📍 Endereço: {contract_address}")
                logger.info(f"  ⛽ Gas usado: {receipt.gasUsed:,}")
                logger.info(f"  🔗 Explorer: {network_config.explorer_url}/address/{contract_address}")
                
                return contract_address
            else:
                logger.error(f"  ❌ Deployment falhou!")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no deployment: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def deploy_all(self):
        """Deploy em todas as redes"""
        try:
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.GREEN}🚀 DEPLOYMENT DE CONTRATOS MEV BOT")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
            # Carregar conta
            if not self.load_account():
                return False
            
            # Compilar contrato
            contract_file = "contracts/FlashLoanArbitrageV2.sol"
            
            if not os.path.exists(contract_file):
                logger.error(f"❌ Arquivo não encontrado: {contract_file}")
                return False
            
            contract_interface = self.compile_contract(contract_file)
            
            if not contract_interface:
                logger.error("❌ Falha na compilação!")
                return False
            
            # Salvar ABI
            os.makedirs("data", exist_ok=True)
            with open("data/contract_abi.json", 'w') as f:
                json.dump(contract_interface['abi'], f, indent=2)
            logger.info("💾 ABI salva em data/contract_abi.json")
            
            # Deploy em cada rede
            for network_name, network_config in self.networks.items():
                contract_address = self.deploy_to_network(
                    network_name,
                    network_config,
                    contract_interface
                )
                
                if contract_address:
                    self.deployed_contracts[network_name] = contract_address
                
                time.sleep(2)  # Pausa entre deployments
            
            # Salvar endereços
            if self.deployed_contracts:
                with open("data/deployed_contracts.json", 'w') as f:
                    json.dump(self.deployed_contracts, f, indent=2)
                
                logger.success("\n✅ Deployment completo!")
                logger.info("\n📋 Contratos deployados:")
                for network, address in self.deployed_contracts.items():
                    logger.info(f"  • {network}: {address}")
                
                logger.info("\n💾 Endereços salvos em data/deployed_contracts.json")
                return True
            else:
                logger.error("\n❌ Nenhum contrato foi deployado!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Função principal"""
    try:
        deployer = ContractDeployer()
        success = deployer.deploy_all()
        
        if success:
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}🎉 DEPLOYMENT CONCLUÍDO COM SUCESSO!")
            print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
            return 0
        else:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}❌ DEPLOYMENT FALHOU!")
            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}\n")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Deployment interrompido pelo usuário!")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
