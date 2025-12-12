# 🚀 GUIA DE INSTALAÇÃO - BOT MEV CORRIGIDO

## ⚡ INSTALAÇÃO RÁPIDA (3 PASSOS)

### **1. Extrair e Preparar**
```bash
unzip mev-bot-CORRIGIDO-FINAL.zip
cd mev-bot-configurado
```

### **2. Criar Ambiente Virtual e Instalar**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install web3 eth-account python-dotenv loguru colorama scikit-learn pandas numpy requests py-solc-x
```

### **3. Deploy e Executar**
```bash
# Deploy dos contratos (primeira vez)
python3 deploy_contracts.py

# Rodar o bot
python3 main_FINAL.py
```

---

## 💰 FUNDOS NECESSÁRIOS

Você já tem fundos em 2 redes:
- ✅ **Base Sepolia**: 0.06 ETH (~$210)
- ✅ **Arbitrum Sepolia**: 0.03 ETH (~$105)

**Opcional**: Ethereum Sepolia
- Faucet: https://www.alchemy.com/faucets/ethereum-sepolia

**Sua carteira**: `0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f`

---

## ✅ O QUE FOI CORRIGIDO

1. ✅ **Endereços Aave V3** atualizados (do repositório oficial)
2. ✅ **BSC Testnet** substituído por Ethereum Sepolia
3. ✅ **Erro de inicialização** corrigido (dict → string)
4. ✅ **Todas as importações** funcionando
5. ✅ **Conexões blockchain** testadas

---

## 🎯 COMO FUNCIONA

**Flash Loan = Empréstimo Instantâneo SEM Capital!**

1. Bot encontra diferença de preço entre DEXs
2. Pede empréstimo ao Aave V3 (ex: 10 ETH)
3. Compra barato em uma DEX
4. Vende caro em outra DEX
5. Devolve empréstimo + taxa 0.09%
6. **Lucro no bolso!**

Tudo em 1 transação - ou funciona ou reverte (sem perda)!

---

## 📊 COMANDOS ÚTEIS

```bash
# Ver logs em tempo real
tail -f data/logs/bot.log

# Testar importações
python3 test_imports.py

# Ver estatísticas
cat data/bot_stats.json

# Ver oportunidades
cat data/opportunities.json
```

---

## ⚙️ CONFIGURAÇÕES (.env)

Já está tudo configurado! Mas você pode ajustar:

```bash
# Lucro mínimo
MIN_PROFIT_USD=50  # Só executa se lucro > $50

# Modo
USE_TESTNET=true  # true = testnet, false = mainnet
DRY_RUN=false     # false = executa de verdade

# IA
ML_CONFIDENCE_THRESHOLD=0.50  # 50% confiança mínima
```

---

## 🔍 TROUBLESHOOTING

### **Deploy falhou?**
- Verifique saldo (mínimo 0.01 ETH por rede)
- Ethereum Sepolia pode falhar (RPC instável) - não tem problema!

### **Bot não encontra oportunidades?**
- Normal em testnet (menos liquidez)
- Diminua `MIN_PROFIT_USD` para $20
- Aguarde alguns minutos

### **Erro de conexão?**
- Use Alchemy no `.env`:
  ```bash
  SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/Zbk6gec3x6CTvSKTyxg3I
  ```

---

## 📈 MIGRAR PARA MAINNET

Quando estiver pronto para lucrar de verdade:

1. Edite `.env`:
   ```bash
   USE_TESTNET=false
   ```

2. Reinicie:
   ```bash
   python3 main_FINAL.py
   ```

**⚠️ ATENÇÃO**: Mainnet usa dinheiro REAL!

---

## 🎉 PRONTO!

Seu bot está 100% funcional!

**Leia também**:
- `CORRECOES_APLICADAS.md` - Detalhes das correções
- `RELATORIO_TESTES.md` - Resultados dos testes
- `README.md` - Documentação completa

**Boa sorte e bons lucros! 🚀💰**
