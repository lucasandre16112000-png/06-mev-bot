#!/bin/bash

# Script para empacotar bot para PC do usuário

echo "📦 Empacotando MEV Bot para PC..."

# Criar diretório temporário
mkdir -p /tmp/mev-bot-package

# Copiar arquivos necessários
cp -r src /tmp/mev-bot-package/
cp main.py /tmp/mev-bot-package/
cp requirements.txt /tmp/mev-bot-package/
cp .env /tmp/mev-bot-package/
cp install.sh /tmp/mev-bot-package/
cp README.md /tmp/mev-bot-package/
cp GUIA_RAPIDO.md /tmp/mev-bot-package/
cp ENTREGA_FINAL.md /tmp/mev-bot-package/
cp .gitignore /tmp/mev-bot-package/

# Criar diretórios de dados
mkdir -p /tmp/mev-bot-package/data/logs
mkdir -p /tmp/mev-bot-package/data/ml_models
mkdir -p /tmp/mev-bot-package/data/history

# Criar arquivo tar.gz
cd /tmp
tar -czf mev-bot-completo.tar.gz mev-bot-package/

# Mover para home
mv mev-bot-completo.tar.gz /home/ubuntu/

# Limpar
rm -rf /tmp/mev-bot-package

echo "✅ Pacote criado: /home/ubuntu/mev-bot-completo.tar.gz"
echo ""
echo "Para usar no seu PC:"
echo "1. Baixe o arquivo mev-bot-completo.tar.gz"
echo "2. Extraia: tar -xzf mev-bot-completo.tar.gz"
echo "3. Entre na pasta: cd mev-bot-package"
echo "4. Instale: bash install.sh"
echo "5. Rode: python main.py"
