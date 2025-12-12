#!/usr/bin/env python3
"""
Análise profunda do código MEV Bot
Verifica se é real ou fake
"""

import os
import re
import json

def analyze_code_authenticity():
    """Analisa autenticidade do código"""
    
    findings = {
        "real_features": [],
        "fake_features": [],
        "suspicious_patterns": [],
        "execution_modes": {},
        "smart_contracts": {},
        "dependencies": []
    }
    
    # 1. Analisar main_FINAL.py
    print("=" * 80)
    print("ANÁLISE DO ARQUIVO PRINCIPAL")
    print("=" * 80)
    
    with open('main_FINAL.py', 'r') as f:
        main_content = f.read()
        
    # Verificar modos de execução
    if 'DRY_RUN' in main_content:
        findings["execution_modes"]["dry_run"] = "PRESENTE - Modo simulação disponível"
    if 'USE_TESTNET' in main_content:
        findings["execution_modes"]["testnet"] = "PRESENTE - Pode rodar em testnet"
    if 'MAINNET' in main_content:
        findings["execution_modes"]["mainnet"] = "PRESENTE - Pode rodar em mainnet"
        
    # Verificar importações reais
    if 'from web3 import Web3' in main_content:
        findings["real_features"].append("✅ Importa Web3 - biblioteca real de blockchain")
    if 'RealFlashLoanStrategy' in main_content:
        findings["real_features"].append("✅ Usa RealFlashLoanStrategy - estratégia real")
    if 'AdvancedMLEngine' in main_content:
        findings["real_features"].append("✅ Usa AdvancedMLEngine - IA avançada")
        
    # 2. Analisar real_flashloan.py
    print("\n" + "=" * 80)
    print("ANÁLISE DA ESTRATÉGIA FLASH LOAN")
    print("=" * 80)
    
    with open('src/strategies/real_flashloan.py', 'r') as f:
        flashloan_content = f.read()
        
    # Verificar execução real
    if 'send_transaction' in flashloan_content or 'sendTransaction' in flashloan_content:
        findings["real_features"].append("✅ Código de envio de transação REAL presente")
    if 'build_transaction' in flashloan_content:
        findings["real_features"].append("✅ Constrói transações reais")
    if 'sign_transaction' in flashloan_content:
        findings["real_features"].append("✅ Assina transações com chave privada")
        
    # Verificar simulação
    if 'simulate' in flashloan_content.lower():
        findings["fake_features"].append("⚠️ Contém código de simulação")
    if 'DRY_RUN' in flashloan_content:
        findings["fake_features"].append("⚠️ Verifica modo DRY_RUN antes de executar")
        
    # 3. Analisar contratos Solidity
    print("\n" + "=" * 80)
    print("ANÁLISE DOS CONTRATOS SOLIDITY")
    print("=" * 80)
    
    sol_files = []
    for root, dirs, files in os.walk('contracts'):
        for file in files:
            if file.endswith('.sol'):
                sol_files.append(os.path.join(root, file))
                
    findings["smart_contracts"]["total"] = len(sol_files)
    findings["smart_contracts"]["files"] = sol_files
    
    # Analisar FlashLoanArbitrageV2.sol
    if os.path.exists('contracts/FlashLoanArbitrageV2.sol'):
        with open('contracts/FlashLoanArbitrageV2.sol', 'r') as f:
            contract_content = f.read()
            
        if 'executeArbitrage' in contract_content:
            findings["real_features"].append("✅ Contrato tem função executeArbitrage")
        if 'flashLoanSimple' in contract_content:
            findings["real_features"].append("✅ Usa Aave Flash Loan (protocolo real)")
        if 'IPool' in contract_content:
            findings["real_features"].append("✅ Interface Aave Pool presente")
        if 'ISwapRouter' in contract_content:
            findings["real_features"].append("✅ Interface Swap Router (Uniswap/PancakeSwap)")
            
        # Verificar proteções
        if 'nonReentrant' in contract_content:
            findings["real_features"].append("✅ Proteção contra reentrancy")
        if 'onlyOwner' in contract_content:
            findings["real_features"].append("✅ Controle de acesso (onlyOwner)")
            
    # 4. Verificar dependências
    print("\n" + "=" * 80)
    print("ANÁLISE DE DEPENDÊNCIAS")
    print("=" * 80)
    
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            deps = f.read()
            
        if 'web3' in deps:
            findings["dependencies"].append("✅ web3.py - biblioteca oficial Ethereum")
        if 'eth-account' in deps:
            findings["dependencies"].append("✅ eth-account - gerenciamento de contas")
        if 'scikit-learn' in deps or 'sklearn' in deps:
            findings["dependencies"].append("✅ scikit-learn - machine learning real")
        if 'xgboost' in deps:
            findings["dependencies"].append("✅ XGBoost - IA avançada")
        if 'tensorflow' in deps or 'torch' in deps:
            findings["dependencies"].append("✅ Deep Learning (TensorFlow/PyTorch)")
            
    # 5. Padrões suspeitos
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO DE PADRÕES SUSPEITOS")
    print("=" * 80)
    
    # Verificar se sempre retorna lucro fake
    all_py_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                all_py_files.append(os.path.join(root, file))
                
    for py_file in all_py_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Verificar lucros hardcoded
            if re.search(r'profit.*=.*random', content, re.IGNORECASE):
                findings["suspicious_patterns"].append(f"⚠️ {py_file}: Lucro gerado aleatoriamente")
            if re.search(r'profit.*=.*\d+\.\d+', content) and 'calculate' not in content:
                findings["suspicious_patterns"].append(f"⚠️ {py_file}: Lucro pode estar hardcoded")
                
        except:
            pass
            
    return findings

def print_findings(findings):
    """Imprime resultados da análise"""
    
    print("\n" + "=" * 80)
    print("RESUMO DA ANÁLISE")
    print("=" * 80)
    
    print("\n🟢 CARACTERÍSTICAS REAIS:")
    for feature in findings["real_features"]:
        print(f"  {feature}")
        
    print(f"\nTotal: {len(findings['real_features'])} características reais encontradas")
    
    print("\n🟡 CARACTERÍSTICAS DE SIMULAÇÃO/FAKE:")
    for feature in findings["fake_features"]:
        print(f"  {feature}")
        
    print(f"\nTotal: {len(findings['fake_features'])} características de simulação")
    
    print("\n🔴 PADRÕES SUSPEITOS:")
    if findings["suspicious_patterns"]:
        for pattern in findings["suspicious_patterns"]:
            print(f"  {pattern}")
    else:
        print("  ✅ Nenhum padrão suspeito detectado")
        
    print("\n📋 MODOS DE EXECUÇÃO:")
    for mode, status in findings["execution_modes"].items():
        print(f"  • {mode}: {status}")
        
    print("\n📜 CONTRATOS SOLIDITY:")
    print(f"  • Total: {findings['smart_contracts']['total']} arquivos")
    for sol_file in findings["smart_contracts"]["files"]:
        print(f"    - {sol_file}")
        
    print("\n📦 DEPENDÊNCIAS:")
    for dep in findings["dependencies"]:
        print(f"  {dep}")
        
    # CONCLUSÃO
    print("\n" + "=" * 80)
    print("CONCLUSÃO")
    print("=" * 80)
    
    real_count = len(findings["real_features"])
    fake_count = len(findings["fake_features"])
    suspicious_count = len(findings["suspicious_patterns"])
    
    print(f"\n📊 Score de Autenticidade:")
    print(f"  • Características Reais: {real_count}")
    print(f"  • Características Fake: {fake_count}")
    print(f"  • Padrões Suspeitos: {suspicious_count}")
    
    if real_count > 10 and fake_count <= 3 and suspicious_count == 0:
        print("\n✅ VEREDICTO: CÓDIGO REAL COM CAPACIDADE DE EXECUÇÃO")
        print("   O código possui infraestrutura real para executar arbitragem")
        print("   MAS possui modos de simulação (DRY_RUN) para testes seguros")
    elif real_count > 5:
        print("\n⚠️ VEREDICTO: CÓDIGO HÍBRIDO (REAL + SIMULAÇÃO)")
        print("   O código pode executar operações reais OU simuladas")
        print("   Depende da configuração (DRY_RUN, USE_TESTNET)")
    else:
        print("\n❌ VEREDICTO: CÓDIGO PREDOMINANTEMENTE FAKE/SIMULADO")
        
    # Salvar resultados
    with open('analysis_report.json', 'w') as f:
        json.dump(findings, f, indent=2)
    
    print("\n💾 Relatório completo salvo em: analysis_report.json")

if __name__ == "__main__":
    findings = analyze_code_authenticity()
    print_findings(findings)
