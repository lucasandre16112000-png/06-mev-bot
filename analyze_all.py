import os
import json

def analyze_file(filepath):
    """Analisa um arquivo e retorna informações básicas"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
        return {
            'path': filepath,
            'size': len(content),
            'lines': len(lines),
            'has_imports': 'import ' in content,
            'has_web3': 'web3' in content.lower() or 'Web3' in content,
            'has_flashloan': 'flashloan' in content.lower() or 'flash_loan' in content.lower(),
            'has_simulation': 'simulat' in content.lower() or 'fake' in content.lower() or 'mock' in content.lower(),
            'has_real_execution': 'send_transaction' in content or 'sendTransaction' in content or 'build_transaction' in content,
            'has_dry_run': 'dry_run' in content.lower() or 'DRY_RUN' in content,
            'has_testnet': 'testnet' in content.lower() or 'TESTNET' in content,
            'has_mainnet': 'mainnet' in content.lower() or 'MAINNET' in content
        }
    except Exception as e:
        return {'path': filepath, 'error': str(e)}

# Analisar todos os arquivos Python
results = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            results.append(analyze_file(filepath))

# Salvar resultados
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Analisados {len(results)} arquivos Python")
print("\nResumo:")
print(f"- Arquivos com Web3: {sum(1 for r in results if r.get('has_web3', False))}")
print(f"- Arquivos com FlashLoan: {sum(1 for r in results if r.get('has_flashloan', False))}")
print(f"- Arquivos com simulação/fake: {sum(1 for r in results if r.get('has_simulation', False))}")
print(f"- Arquivos com execução real: {sum(1 for r in results if r.get('has_real_execution', False))}")
