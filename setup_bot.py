#!/usr/bin/env python3
"""
🚀 CONFIGURAÇÃO AUTOMÁTICA DO BOT
"""

import json
import os

def create_deployment_file():
    """Cria arquivo de contratos para o bot funcionar"""
    
    print("=" * 80)
    print("🚀 CONFIGURAÇÃO AUTOMÁTICA DO MEV BOT")
    print("=" * 80)
    
    # Criar arquivo de contratos deployados
    deployed_contracts = {
        "base_sepolia": {
            "FlashLoanArbitrageV2": "0x0000000000000000000000000000000000000000",
            "deployed": False,
            "note": "Para deployment real, execute: python deploy_contracts.py"
        },
        "arbitrum_sepolia": {
            "FlashLoanArbitrageV2": "0x0000000000000000000000000000000000000000",
            "deployed": False,
            "note": "Para deployment real, execute: python deploy_contracts.py"
        },
        "bsc_testnet": {
            "FlashLoanArbitrageV2": "0x0000000000000000000000000000000000000000",
            "deployed": False,
            "note": "Para deployment real, execute: python deploy_contracts.py"
        }
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/deployed_contracts.json', 'w') as f:
        json.dump(deployed_contracts, f, indent=2)
    
    print("\n✅ Arquivo data/deployed_contracts.json criado!")
    
    # Atualizar .env para modo simulação
    print("\n📝 Configurando .env para MODO SIMULAÇÃO...")
    
    env_content = []
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('DRY_RUN='):
                env_content.append('DRY_RUN=true\n')
                print("   ✅ DRY_RUN=true (modo simulação ativado)")
            else:
                env_content.append(line)
    
    with open('.env', 'w') as f:
        f.writelines(env_content)
    
    return deployed_contracts

def print_instructions():
    """Imprime instruções de uso"""
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 80)
    
    print("\n🎯 O BOT ESTÁ CONFIGURADO EM MODO SIMULAÇÃO")
    print("\nIsso significa:")
    print("  ✅ Vai conectar nas blockchains")
    print("  ✅ Vai buscar oportunidades reais")
    print("  ✅ IA vai analisar as oportunidades")
    print("  ❌ NÃO vai enviar transações (apenas simula)")
    print("  ❌ NÃO vai gastar gas")
    
    print("\n📋 COMO USAR:")
    print("\n1. RODAR O BOT EM MODO SIMULAÇÃO:")
    print("   python main_FINAL.py")
    print("   ou")
    print("   python3 main_FINAL.py")
    
    print("\n2. O BOT VAI:")
    print("   • Conectar nas redes (Base, Arbitrum, BSC)")
    print("   • Buscar diferenças de preço entre DEXs")
    print("   • Mostrar oportunidades encontradas")
    print("   • Simular execução (sem gastar nada)")
    
    print("\n3. PARA EXECUTAR DE VERDADE (TESTNET):")
    print("   • Edite .env e mude: DRY_RUN=false")
    print("   • Pegue ETH/BNB grátis nos faucets:")
    print("     - Base: https://www.alchemy.com/faucets/base-sepolia")
    print("     - Arbitrum: https://www.alchemy.com/faucets/arbitrum-sepolia")
    print("     - BSC: https://testnet.bnbchain.org/faucet-smart")
    print("   • Execute: python deploy_contracts.py")
    print("   • Execute: python main_FINAL.py")
    
    print("\n💡 DICA:")
    print("   Comece em modo simulação para entender como funciona!")
    print("   Depois passe para testnet (dinheiro fake)")
    print("   Só vá para mainnet quando tiver certeza!")
    
    print("\n📊 SUA CARTEIRA:")
    print("   Endereço: 0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f")
    print("   Verifique saldo em:")
    print("   • https://sepolia.basescan.org/address/0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f")
    
    print("\n" + "=" * 80)
    print()

if __name__ == "__main__":
    create_deployment_file()
    print_instructions()
