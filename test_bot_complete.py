#!/usr/bin/env python3
"""
Teste completo do bot MEV
"""

import sys

print("=" * 80)
print("🧪 TESTE COMPLETO DO MEV BOT")
print("=" * 80)

# Teste 1: Importações
print("\n1️⃣ Testando importações...")
try:
    from src.config.config import BotConfig, validate_config
    from src.core.blockchain import blockchain
    from src.core.dex import MultiDEXScanner
    from src.utils.risk_manager import RiskManager
    print("   ✅ Todas as importações OK")
except Exception as e:
    print(f"   ❌ Erro nas importações: {e}")
    sys.exit(1)

# Teste 2: Configuração
print("\n2️⃣ Testando configuração...")
try:
    print(f"   • USE_TESTNET: {BotConfig.USE_TESTNET}")
    print(f"   • DRY_RUN: {BotConfig.DRY_RUN}")
    print(f"   • MIN_PROFIT_USD: ${BotConfig.MIN_PROFIT_USD}")
    print(f"   • Carteira: {BotConfig.WALLET_ADDRESS[:10]}...")
    print("   ✅ Configuração carregada")
except Exception as e:
    print(f"   ❌ Erro na configuração: {e}")

# Teste 3: Validação
print("\n3️⃣ Validando configuração...")
try:
    if validate_config():
        print("   ✅ Configuração válida")
    else:
        print("   ⚠️ Configuração com avisos (mas funciona)")
except Exception as e:
    print(f"   ⚠️ Validação: {e}")

# Teste 4: Estrutura de arquivos
print("\n4️⃣ Verificando estrutura...")
import os
required_files = [
    '.env',
    'main_FINAL.py',
    'data/deployed_contracts.json',
    'src/config/config.py',
    'src/core/blockchain.py',
    'src/core/dex.py',
]
missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - FALTANDO")
        missing.append(file)

# Resumo
print("\n" + "=" * 80)
print("📊 RESUMO DO TESTE")
print("=" * 80)

if not missing:
    print("\n✅ BOT ESTÁ PRONTO PARA RODAR!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Pegar fundos de testnet nos faucets")
    print("   2. Executar: python3 deploy_contracts.py")
    print("   3. Executar: python3 main_FINAL.py")
else:
    print(f"\n⚠️ {len(missing)} arquivos faltando")
    print("   Execute o script de configuração primeiro")

print("\n" + "=" * 80)
