#!/usr/bin/env python3
"""
🧪 TESTE DAS CORREÇÕES HÍBRIDAS
Valida se todas as correções foram aplicadas corretamente
"""

import os
import sys
from loguru import logger

def test_files_exist():
    """Testa se todos os arquivos híbridos existem"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 1: Verificando arquivos híbridos...")
    logger.info("="*60)
    
    required_files = [
        "contracts/FlashLoanArbitrageHybrid.sol",
        "deploy_contracts_hybrid.py",
        "main_hybrid.py",
        "src/strategies/real_flashloan_hybrid.py",
        "README_HYBRID.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            logger.success(f"✅ {file_path}")
        else:
            logger.error(f"❌ {file_path} NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def test_requirements():
    """Testa se requirements.txt foi atualizado"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 2: Verificando requirements.txt...")
    logger.info("="*60)
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    checks = {
        "xgboost": "xgboost" in content,
        "joblib": "joblib" in content,
        "scikit-learn": "scikit-learn" in content
    }
    
    all_ok = True
    for package, exists in checks.items():
        if exists:
            logger.success(f"✅ {package} presente")
        else:
            logger.error(f"❌ {package} FALTANDO")
            all_ok = False
    
    return all_ok

def test_contract_hybrid():
    """Testa se o contrato híbrido tem as funções corretas"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 3: Verificando contrato híbrido...")
    logger.info("="*60)
    
    with open("contracts/FlashLoanArbitrageHybrid.sol", "r") as f:
        content = f.read()
    
    checks = {
        "Modo híbrido": "useExternalDEX" in content,
        "Função getMode": "function getMode()" in content,
        "Compatibilidade Aave": "IPool" in content,
        "Compatibilidade Uniswap": "ISwapRouter" in content,
        "Modo Aave-Only": "AAVE-ONLY" in content
    }
    
    all_ok = True
    for feature, exists in checks.items():
        if exists:
            logger.success(f"✅ {feature}")
        else:
            logger.error(f"❌ {feature} FALTANDO")
            all_ok = False
    
    return all_ok

def test_deploy_script():
    """Testa se o script de deploy está configurado corretamente"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 4: Verificando script de deploy...")
    logger.info("="*60)
    
    with open("deploy_contracts_hybrid.py", "r") as f:
        content = f.read()
    
    checks = {
        "Base Sepolia": "base_sepolia" in content,
        "Arbitrum Sepolia": "arbitrum_sepolia" in content,
        "Ethereum Sepolia": '"sepolia"' in content,
        "Detecção de Uniswap": "has_uniswap" in content,
        "Modo híbrido": "FlashLoanArbitrageHybrid" in content
    }
    
    all_ok = True
    for feature, exists in checks.items():
        if exists:
            logger.success(f"✅ {feature}")
        else:
            logger.error(f"❌ {feature} FALTANDO")
            all_ok = False
    
    return all_ok

def test_strategy_hybrid():
    """Testa se a estratégia híbrida está correta"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 5: Verificando estratégia híbrida...")
    logger.info("="*60)
    
    with open("src/strategies/real_flashloan_hybrid.py", "r") as f:
        content = f.read()
    
    checks = {
        "Classe HybridFlashLoanExecutor": "class HybridFlashLoanExecutor" in content,
        "Classe HybridFlashLoanStrategy": "class HybridFlashLoanStrategy" in content,
        "Suporte a modo híbrido": "FlashLoanArbitrageHybrid" in content,
        "Detecção de modo": "getMode" in content
    }
    
    all_ok = True
    for feature, exists in checks.items():
        if exists:
            logger.success(f"✅ {feature}")
        else:
            logger.error(f"❌ {feature} FALTANDO")
            all_ok = False
    
    return all_ok

def test_main_hybrid():
    """Testa se o main híbrido está correto"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 6: Verificando main híbrido...")
    logger.info("="*60)
    
    with open("main_hybrid.py", "r") as f:
        content = f.read()
    
    checks = {
        "Classe MEVBotHybrid": "class MEVBotHybrid" in content,
        "Import estratégia híbrida": "from src.strategies.real_flashloan_hybrid import HybridFlashLoanStrategy" in content,
        "Banner híbrido": "VERSÃO HÍBRIDA" in content
    }
    
    all_ok = True
    for feature, exists in checks.items():
        if exists:
            logger.success(f"✅ {feature}")
        else:
            logger.error(f"❌ {feature} FALTANDO")
            all_ok = False
    
    return all_ok

def test_imports():
    """Testa se os imports funcionam"""
    logger.info("\n" + "="*60)
    logger.info("🧪 TESTE 7: Testando imports...")
    logger.info("="*60)
    
    tests = []
    
    # Testar import da estratégia híbrida
    try:
        from src.strategies.real_flashloan_hybrid import HybridFlashLoanStrategy, HybridFlashLoanExecutor
        logger.success("✅ Import estratégia híbrida")
        tests.append(True)
    except Exception as e:
        logger.error(f"❌ Erro ao importar estratégia híbrida: {e}")
        tests.append(False)
    
    # Testar import de config
    try:
        from src.config.config import BotConfig
        logger.success("✅ Import config")
        tests.append(True)
    except Exception as e:
        logger.error(f"❌ Erro ao importar config: {e}")
        tests.append(False)
    
    # Testar import de blockchain
    try:
        from src.core.blockchain import blockchain
        logger.success("✅ Import blockchain")
        tests.append(True)
    except Exception as e:
        logger.error(f"❌ Erro ao importar blockchain: {e}")
        tests.append(False)
    
    return all(tests)

def main():
    """Executa todos os testes"""
    logger.info("\n" + "="*60)
    logger.info("🧪 VALIDAÇÃO DAS CORREÇÕES HÍBRIDAS")
    logger.info("="*60)
    
    tests = [
        ("Arquivos híbridos", test_files_exist),
        ("Requirements.txt", test_requirements),
        ("Contrato híbrido", test_contract_hybrid),
        ("Script de deploy", test_deploy_script),
        ("Estratégia híbrida", test_strategy_hybrid),
        ("Main híbrido", test_main_hybrid),
        ("Imports Python", test_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Erro no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            logger.success(f"✅ {test_name}")
        else:
            logger.error(f"❌ {test_name}")
    
    logger.info("\n" + "="*60)
    if passed == total:
        logger.success(f"🎉 TODOS OS TESTES PASSARAM! ({passed}/{total})")
        logger.success("✅ Correções híbridas validadas com sucesso!")
        logger.info("\n💡 Próximos passos:")
        logger.info("   1. python deploy_contracts_hybrid.py")
        logger.info("   2. python main_hybrid.py")
    else:
        logger.error(f"⚠️ ALGUNS TESTES FALHARAM: {passed}/{total}")
        logger.error("❌ Verifique os erros acima")
    logger.info("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
