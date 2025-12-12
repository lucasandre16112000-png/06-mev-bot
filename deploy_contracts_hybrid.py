#!/usr/bin/env python3
"""
🚀 DEPLOYMENT HÍBRIDO DE CONTRATOS
Deploy inteligente que adapta o contrato para cada rede
✅ Múltiplos RPCs com fallback automático
✅ Gas price otimizado (1.5x)
✅ Timeout reduzido (120s)
"""

import json
import os
import time
from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
from loguru import logger
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de rede HÍBRIDAS com MÚLTIPLOS RPCs
NETWORKS = {
    "base_sepolia": {
        "name": "Base Sepolia",
        "rpcs": [  # Múltiplos RPCs em ordem de prioridade
            "https://base-sepolia.gateway.tenderly.co",
            "https://base-sepolia-rpc.publicnode.com",
            "https://sepolia.base.org"
        ],
        "chain_id": 84532,
        "aave_pool": "0x07eA79F68B2B3df564D0A34F8e19D9B1e339814b",
        "uniswap_router": "0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4",
        "has_uniswap": True,  # ✅ Tem Uniswap V3
        "explorer": "https://sepolia.basescan.org"
    },
    "arbitrum_sepolia": {
        "name": "Arbitrum Sepolia",
        "rpcs": [
            "https://arbitrum-sepolia-rpc.publicnode.com",
            "https://sepolia-rollup.arbitrum.io/rpc"
        ],
        "chain_id": 421614,
        "aave_pool": "0xBfC91D59fdAA134A4ED45f7B584cAf96D7792Eff",
        "uniswap_router": "0x101F443B4d1b059569D643917553c771E1b9663E",
        "has_uniswap": True,  # ✅ Tem Uniswap V3
        "explorer": "https://sepolia.arbiscan.io"
    },
    "sepolia": {
        "name": "Ethereum Sepolia",
        "rpcs": [
            "https://sepolia.gateway.tenderly.co",
            "https://ethereum-sepolia-rpc.publicnode.com"
        ],
        "chain_id": 11155111,
        "aave_pool": "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951",
        "uniswap_router": "0x0000000000000000000000000000000000000000",  # ❌ NÃO TEM
        "has_uniswap": False,  # ❌ Modo Aave-Only
        "explorer": "https://sepolia.etherscan.io"
    }
}

def load_account():
    """Carrega conta da carteira"""
    private_key = os.getenv("PRIVATE_KEY")
    account = Account.from_key(private_key)
    logger.info(f"✅ Conta carregada: {account.address}")
    return account

def compile_contract():
    """Compila o contrato híbrido"""
    logger.info("📝 Compilando contracts/FlashLoanArbitrageHybrid.sol...")
    
    # Instalar versão correta do solc
    install_solc("0.8.20")
    
    # Ler contrato principal
    with open("contracts/FlashLoanArbitrageHybrid.sol", "r") as f:
        contract_source = f.read()
    
    # Ler interfaces
    interfaces = {}
    interface_files = [
        "IPoolAddressesProvider.sol",
        "IPool.sol",
        "IERC20.sol",
        "ISwapRouter.sol"
    ]
    
    for interface_file in interface_files:
        path = f"contracts/interfaces/{interface_file}"
        with open(path, "r") as f:
            interfaces[f"contracts/interfaces/{interface_file}"] = {
                "content": f.read()
            }
    
    # Compilar com otimizador IR
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {
                "contracts/FlashLoanArbitrageHybrid.sol": {"content": contract_source},
                **interfaces
            },
            "settings": {
                "optimizer": {
                    "enabled": True,
                    "runs": 200
                },
                "viaIR": True,  # ✅ Resolve Stack too deep
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            }
        },
        solc_version="0.8.20"
    )
    
    # Extrair ABI e bytecode
    contract_data = compiled_sol["contracts"]["contracts/FlashLoanArbitrageHybrid.sol"]["FlashLoanArbitrageHybrid"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]
    
    logger.success("✅ Contrato compilado com sucesso!")
    logger.info(f"  📏 Tamanho do bytecode: {len(bytecode) // 2} bytes")
    
    return abi, bytecode

def connect_with_fallback(rpcs, network_name):
    """Tenta conectar em múltiplos RPCs até conseguir"""
    for i, rpc in enumerate(rpcs):
        try:
            logger.info(f"🔌 Tentando RPC {i+1}/{len(rpcs)}: {rpc[:50]}...")
            w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 10}))
            
            # Testar conexão
            block = w3.eth.block_number
            logger.success(f"✅ Conectado em {network_name} (bloco: {block})")
            return w3
        except Exception as e:
            logger.warning(f"⚠️ RPC {i+1} falhou: {str(e)[:50]}")
            if i == len(rpcs) - 1:
                raise Exception(f"❌ Todos os RPCs falharam para {network_name}")
            continue

def deploy_to_network(network_key, network_config, abi, bytecode, account):
    """Faz deploy em uma rede específica"""
    try:
        logger.info("\n" + "="*60)
        logger.info(f"🌐 Fazendo deploy em {network_config['name']}...")
        logger.info("="*60)
        
        # Conectar com fallback automático
        w3 = connect_with_fallback(network_config['rpcs'], network_config['name'])
        
        # Verificar saldo
        balance = w3.eth.get_balance(account.address)
        balance_eth = w3.from_wei(balance, 'ether')
        logger.info(f"💰 Saldo: {balance_eth:.4f} ETH")
        
        if balance == 0:
            raise Exception("❌ Saldo insuficiente!")
        
        # Verificar se tem Uniswap
        aave_pool = network_config['aave_pool']
        uniswap_router = network_config['uniswap_router']
        
        if not network_config['has_uniswap']:
            logger.warning(f"⚠️ {network_config['name']} não tem Uniswap V3")
            logger.info("✅ Usando modo AAVE-ONLY (somente Flash Loans)")
        
        # Log dos endereços
        logger.info(f"📍 Aave Pool: {aave_pool}")
        if network_config['has_uniswap']:
            logger.info(f"📍 Uniswap Router: {uniswap_router}")
        else:
            logger.info(f"📍 Uniswap Router: DESABILITADO (address(0))")
        
        # Construir transação
        logger.info("📝 Construindo transação de deployment...")
        
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Determinar se deve usar DEX externa (bool)
        use_external_dex = network_config['has_uniswap']
        
        # Gas price otimizado (1.5x para garantir mineração rápida)
        gas_price = int(w3.eth.gas_price * 1.5)
        logger.info(f"⛽ Gas price: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei (1.5x)")
        
        constructor_txn = contract.constructor(
            aave_pool,
            use_external_dex
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': gas_price,
            'chainId': network_config['chain_id']
        })
        
        # Assinar
        logger.info("✍️ Assinando transação...")
        signed_txn = w3.eth.account.sign_transaction(constructor_txn, account.key)
        
        # Enviar
        logger.info("📤 Enviando transação...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        logger.info(f"⏳ Aguardando confirmação... (tx: {tx_hash_hex[-64:]})")
        
        # Aguardar confirmação (timeout reduzido para 120s)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            contract_address = receipt.contractAddress
            logger.success(f"✅ Deploy bem-sucedido!")
            logger.success(f"📍 Endereço do contrato: {contract_address}")
            logger.info(f"⛽ Gas usado: {receipt.gasUsed}")
            logger.info(f"🔗 Explorer: {network_config['explorer']}/address/{contract_address}")
            
            # Aguardar propagação do contrato
            logger.info("⏳ Aguardando propagação do contrato...")
            time.sleep(3)
            
            # Verificar modo (com retry)
            mode = "Unknown"
            try:
                deployed_contract = w3.eth.contract(address=contract_address, abi=abi)
                mode = deployed_contract.functions.getMode().call()
                logger.info(f"🎯 Modo: {mode}")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível verificar modo: {str(e)[:50]}")
                # Determinar modo baseado na configuração
                mode = "HYBRID: Aave + External DEX" if network_config['has_uniswap'] else "AAVE-ONLY: Flash Loan Only"
                logger.info(f"🎯 Modo (baseado em config): {mode}")
            
            time.sleep(1)
            
            return {
                "address": contract_address,
                "tx_hash": tx_hash_hex,
                "mode": mode,
                "success": True
            }
        else:
            raise Exception("❌ Transação revertida!")
            
    except Exception as e:
        logger.error(f"❌ Erro no deploy: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def save_addresses(deployed_contracts, abi):
    """Salva endereços deployados"""
    # Salvar endereços
    with open("data/deployed_contracts.json", "w") as f:
        json.dump(deployed_contracts, f, indent=2)
    logger.success("✅ Endereços salvos em data/deployed_contracts.json")
    
    # Salvar ABI
    with open("data/FlashLoanArbitrageHybrid_ABI.json", "w") as f:
        json.dump(abi, f, indent=2)
    logger.success("✅ ABI salva em data/FlashLoanArbitrageHybrid_ABI.json")

def main():
    logger.info("\n" + "="*60)
    logger.info("🚀 DEPLOYMENT HÍBRIDO DE CONTRATOS MEV BOT")
    logger.info("="*60)
    
    # Carregar conta
    account = load_account()
    
    # Compilar contrato
    abi, bytecode = compile_contract()
    
    # Deploy em todas as redes
    deployed_contracts = {}
    
    for network_key, network_config in NETWORKS.items():
        result = deploy_to_network(network_key, network_config, abi, bytecode, account)
        deployed_contracts[network_key] = result
    
    # Salvar resultados
    save_addresses(deployed_contracts, abi)
    
    # Resumo
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO DO DEPLOYMENT")
    logger.info("="*60)
    
    success_count = 0
    for network_key, result in deployed_contracts.items():
        if result.get("success"):
            logger.success(f"✅ {network_key}: {result['address']}")
            logger.info(f"   Modo: {result['mode']}")
            success_count += 1
        else:
            logger.error(f"❌ {network_key}: Falhou")
    
    logger.info("\n" + "="*60)
    if success_count == len(NETWORKS):
        logger.success(f"🎉 DEPLOYMENT COMPLETO: {success_count}/{len(NETWORKS)}")
    else:
        logger.warning(f"⚠️ DEPLOYMENT PARCIAL: {success_count}/{len(NETWORKS)}")
    logger.info("="*60)

if __name__ == "__main__":
    main()
