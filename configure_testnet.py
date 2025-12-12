#!/usr/bin/env python3
"""
Configura o bot para TESTNET REAL
"""

def configure_for_testnet():
    print("=" * 80)
    print("🔧 CONFIGURANDO BOT PARA TESTNET REAL")
    print("=" * 80)
    
    # Ler .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Modificar configurações
    new_lines = []
    changes = []
    
    for line in lines:
        if line.startswith('USE_TESTNET='):
            new_lines.append('USE_TESTNET=true\n')
            changes.append("✅ USE_TESTNET=true (redes de teste)")
        elif line.startswith('DRY_RUN='):
            new_lines.append('DRY_RUN=false\n')
            changes.append("✅ DRY_RUN=false (execução REAL em testnet)")
        elif line.startswith('MIN_PROFIT_USD='):
            new_lines.append('MIN_PROFIT_USD=2\n')
            changes.append("✅ MIN_PROFIT_USD=2 (mais permissivo para testnet)")
        elif line.startswith('ML_CONFIDENCE_THRESHOLD='):
            new_lines.append('ML_CONFIDENCE_THRESHOLD=0.50\n')
            changes.append("✅ ML_CONFIDENCE_THRESHOLD=0.50 (mais oportunidades)")
        else:
            new_lines.append(line)
    
    # Salvar
    with open('.env', 'w') as f:
        f.writelines(new_lines)
    
    print("\n📝 Configurações aplicadas:")
    for change in changes:
        print(f"   {change}")
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 80)
    
    print("\n🎯 SEU BOT ESTÁ CONFIGURADO PARA:")
    print("   • Rodar em TESTNET (Base Sepolia, Arbitrum Sepolia, BSC Testnet)")
    print("   • Executar transações REAIS (mas com dinheiro de teste)")
    print("   • Lucro mínimo: $2 (encontra mais oportunidades)")
    print("   • Confiança IA: 50% (mais permissivo)")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1. PEGAR FUNDOS DE TESTNET (GRÁTIS):")
    print("   Sua carteira: 0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f")
    print("\n   Base Sepolia (precisa ~0.05 ETH):")
    print("   → https://www.alchemy.com/faucets/base-sepolia")
    print("\n   Arbitrum Sepolia (precisa ~0.05 ETH):")
    print("   → https://www.alchemy.com/faucets/arbitrum-sepolia")
    print("\n   BSC Testnet (precisa ~0.1 BNB):")
    print("   → https://testnet.bnbchain.org/faucet-smart")
    
    print("\n2. VERIFICAR SALDO:")
    print("   Base: https://sepolia.basescan.org/address/0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f")
    print("   Arbitrum: https://sepolia.arbiscan.io/address/0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f")
    print("   BSC: https://testnet.bscscan.com/address/0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f")
    
    print("\n3. FAZER DEPLOYMENT DOS CONTRATOS:")
    print("   python3 deploy_contracts.py")
    
    print("\n4. RODAR O BOT:")
    print("   python3 main_FINAL.py")
    
    print("\n💡 DICA:")
    print("   Comece pegando fundos em UMA rede primeiro (ex: Base Sepolia)")
    print("   Faça o deployment nessa rede e teste")
    print("   Depois expanda para as outras redes")
    
    print("\n⚠️ LEMBRE-SE:")
    print("   • Testnet = dinheiro FAKE (não vale nada)")
    print("   • Você pode testar à vontade sem riscos")
    print("   • Perfeito para aprender por 1 mês!")
    print()

if __name__ == "__main__":
    configure_for_testnet()
