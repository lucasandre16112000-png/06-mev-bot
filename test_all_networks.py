#!/usr/bin/env python3
"""
Teste completo de todas as redes
"""
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

print("🧪 TESTE COMPLETO DAS 3 REDES")
print("="*60)

networks = {
    "Base Sepolia": os.getenv("BASE_RPC_URL"),
    "Arbitrum Sepolia": os.getenv("ARBITRUM_RPC_URL"),
    "Ethereum Sepolia": os.getenv("SEPOLIA_RPC_URL"),
}

wallet = os.getenv("WALLET_ADDRESS")
print(f"\n💰 Carteira: {wallet}")
print("="*60)

working = 0
total = len(networks)

for name, rpc_url in networks.items():
    try:
        print(f"\n🌐 {name}")
        print(f"   RPC: {rpc_url[:50]}...")
        
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
        
        if w3.is_connected():
            block = w3.eth.block_number
            balance = w3.eth.get_balance(wallet)
            balance_eth = w3.from_wei(balance, 'ether')
            
            print(f"   ✅ CONECTADO!")
            print(f"   📦 Bloco: {block:,}")
            print(f"   💰 Saldo: {balance_eth:.6f} ETH")
            working += 1
        else:
            print(f"   ❌ Não conectou")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:60]}...")

print("\n" + "="*60)
print(f"📊 RESULTADO: {working}/{total} redes funcionando")
print("="*60)

if working == total:
    print("\n🎉 PERFEITO! Todas as redes funcionando!")
elif working >= 2:
    print(f"\n⚠️  {working} redes funcionando (suficiente para operar)")
else:
    print("\n❌ Poucas redes funcionando!")
