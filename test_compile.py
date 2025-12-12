import json
from py_solc_x import compile_source, install_solc

print('=' * 60)
print('📝 TESTANDO COMPILAÇÃO DO CONTRATO')
print('=' * 60)

try:
    # Instalar compilador
    print('⏳ Instalando Solidity 0.8.20...')
    install_solc('0.8.20', show_progress=False)
    print('✅ Compilador instalado!')
    
    # Ler contrato
    with open('contracts/FlashLoanArbitrageV2.sol', 'r') as f:
        contract_source = f.read()
    
    print('✅ Contrato lido: FlashLoanArbitrageV2.sol')
    print(f'   Tamanho: {len(contract_source)} caracteres')
    
    # Compilar
    print('⏳ Compilando contrato...')
    compiled = compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.20'
    )
    
    contract_id = list(compiled.keys())[0]
    abi = compiled[contract_id]['abi']
    bytecode = compiled[contract_id]['bin']
    
    print(f'✅ Compilação bem-sucedida!')
    print(f'   ABI: {len(abi)} funções')
    print(f'   Bytecode: {len(bytecode)} bytes')
    
    print('=' * 60)
    print('✅ TESTE DE COMPILAÇÃO CONCLUÍDO!')
    
except Exception as e:
    print(f'❌ ERRO: {e}')
    import traceback
    traceback.print_exc()
