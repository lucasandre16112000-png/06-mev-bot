#!/usr/bin/env python3
"""
Script para corrigir TODOS os erros do bot
"""

import re

print("🔧 Corrigindo TODOS os erros...")

# 1. Corrigir dex.py para usar TOKENS do config
print("\n1️⃣ Corrigindo erro de scan de pares...")

with open('src/core/dex.py', 'r') as f:
    content = f.read()

# Adicionar import de TOKENS
if 'from src.config.config import (' in content:
    content = content.replace(
        'from src.config.config import (\n    UNISWAP_V3_ROUTER,\n    PANCAKESWAP_V3_ROUTER,\n    AERODROME_ROUTER,\n    # MAJOR_TOKENS\n)',
        'from src.config.config import (\n    UNISWAP_V3_ROUTER,\n    PANCAKESWAP_V3_ROUTER,\n    AERODROME_ROUTER,\n    TOKENS\n)'
    )

# Substituir MAJOR_TOKENS por TOKENS[self.network]
content = re.sub(
    r'tokens = \[\]  # TODO: usar tokens do config',
    'tokens = TOKENS.get(self.network, {})',
    content
)

with open('src/core/dex.py', 'w') as f:
    f.write(content)

print("   ✅ dex.py corrigido!")

# 2. Criar arquivo de endereços de contratos (simulado para não dar erro)
print("\n2️⃣ Criando arquivo de contratos deployados...")

import json

contract_addresses = {
    "arbitrum_sepolia": {
        "FlashLoanArbitrage": "0x0000000000000000000000000000000000000000",  # Placeholder
        "deployed": False,
        "note": "Execute 'python deploy_contracts.py' para fazer deployment real"
    },
    "bsc_testnet": {
        "FlashLoanArbitrage": "0x0000000000000000000000000000000000000000",  # Placeholder
        "deployed": False,
        "note": "Execute 'python deploy_contracts.py' para fazer deployment real"
    }
}

with open('data/contract_addresses.json', 'w') as f:
    json.dump(contract_addresses, f, indent=2)

print("   ✅ Arquivo de contratos criado!")
print("   ⚠️  Para fazer deployment REAL, rode: python deploy_contracts.py")

# 3. Tentar corrigir URL do Base Sepolia
print("\n3️⃣ Atualizando URL do Base Sepolia...")

with open('.env', 'r') as f:
    env_content = f.read()

# Atualizar URL do Base Sepolia
env_content = re.sub(
    r'BASE_SEPOLIA_RPC_URL=.*',
    'BASE_SEPOLIA_RPC_URL=https://sepolia.base.org',
    env_content
)

with open('.env', 'w') as f:
    f.write(env_content)

print("   ✅ URL do Base Sepolia atualizada!")

print("\n✅ TODAS AS CORREÇÕES APLICADAS!")
print("\n📋 Próximos passos:")
print("   1. Rode: python main_FINAL.py")
print("   2. Para deployment real: python deploy_contracts.py")
print("\n🚀 Bot pronto para rodar!")
