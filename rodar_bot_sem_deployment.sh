#!/bin/bash

echo "============================================================"
echo "🚀 RODANDO BOT EM MODO DE ANÁLISE (SEM DEPLOYMENT)"
echo "============================================================"
echo ""
echo "ℹ️  O bot vai:"
echo "   ✅ Conectar nas redes de teste"
echo "   ✅ Buscar oportunidades de arbitragem"
echo "   ✅ Analisar com IA"
echo "   ⚠️  Simular execução (DRY_RUN=true temporário)"
echo ""
echo "   Quando encontrar oportunidades reais, você pode:"
echo "   1. Fazer o deployment correto dos contratos"
echo "   2. Desativar DRY_RUN e executar de verdade"
echo ""
echo "============================================================"
echo ""

# Ativar venv
source venv/bin/activate

# Backup do .env
cp .env .env.backup

# Ativar DRY_RUN temporariamente
sed -i 's/DRY_RUN=false/DRY_RUN=true/' .env

echo "▶️  Iniciando bot..."
echo ""

# Rodar bot
python3 main_FINAL.py

# Restaurar .env
mv .env.backup .env

echo ""
echo "✅ Bot finalizado!"
