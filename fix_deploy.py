#!/usr/bin/env python3
"""
Corrige o arquivo deploy_contracts.py
"""

print("🔧 Corrigindo deploy_contracts.py...")

# Ler arquivo
with open('deploy_contracts.py', 'r') as f:
    content = f.read()

# Fazer a correção
old_imports = """import os
import json
import time
from web3 import Web3
from eth_account import Account
from loguru import logger
from colorama import init, Fore, Style
from solcx import compile_source, install_solc, set_solc_version
import sys"""

new_imports = """import os
import json
import time
from typing import Optional, Dict, List
from web3 import Web3
from eth_account import Account
from loguru import logger
from colorama import init, Fore, Style
from solcx import compile_source, install_solc, set_solc_version
import sys"""

content = content.replace(old_imports, new_imports)

# Salvar
with open('deploy_contracts.py', 'w') as f:
    f.write(content)

print("✅ Arquivo corrigido!")
print("\nAgora execute:")
print("   python3 deploy_contracts.py")
