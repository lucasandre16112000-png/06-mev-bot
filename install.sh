#!/bin/bash

# 🤖 MEV BOT - Script de Instalação Automática

set -e

echo "============================================"
echo "🤖 MEV BOT - Instalação Automática"
echo "============================================"
echo ""

# Verificar Python
echo "📦 Verificando Python..."
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 não encontrado!"
    echo "Por favor, instale Python 3.11 primeiro:"
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "  macOS: brew install python@3.11"
    exit 1
fi

echo "✅ Python 3.11 encontrado!"
echo ""

# Criar ambiente virtual
echo "🔧 Criando ambiente virtual..."
python3.11 -m venv venv

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️ Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo ""
echo "============================================"
echo "✅ Instalação Concluída!"
echo "============================================"
echo ""
echo "🎯 Próximos passos:"
echo ""
echo "1. Ativar ambiente virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Rodar o bot:"
echo "   python main.py"
echo ""
echo "3. (Opcional) Rodar dashboard:"
echo "   cd mev-dashboard && pnpm install && pnpm dev"
echo ""
echo "============================================"
echo "⚠️ IMPORTANTE:"
echo "============================================"
echo ""
echo "• O bot está em modo TESTNET (seguro)"
echo "• Suas credenciais já estão configuradas"
echo "• Você NÃO precisa editar nada!"
echo "• Apenas rode: python main.py"
echo ""
echo "🚀 Boa sorte!"
echo ""
