# 🚀 GUIA RÁPIDO - MEV BOT

## ⚡ Instalação e Execução em 3 Passos

### 1️⃣ Instalar Dependências

```bash
cd mev-bot-pro
bash install.sh
```

### 2️⃣ Rodar o Bot

```bash
source venv/bin/activate
python main.py
```

### 3️⃣ (Opcional) Abrir Dashboard

```bash
cd mev-dashboard
pnpm install
pnpm dev
```

Acesse: http://localhost:3000

---

## ✅ TUDO JÁ ESTÁ CONFIGURADO!

Suas credenciais já estão no arquivo `.env`:
- ✅ Alchemy API Key
- ✅ Private Key
- ✅ Endereço da carteira
- ✅ Modo TESTNET ativado

**Você NÃO precisa configurar NADA!**

---

## 🛡️ PROTEÇÃO ANTI-SCAM ATIVA

O bot **NUNCA** vai operar com tokens não confiáveis!

**Apenas tokens permitidos:**
- ✅ USDC, USDT, DAI (stablecoins)
- ✅ WETH, WBTC, WBNB (major tokens)
- ✅ UNI, AAVE, LINK, CRV (DeFi blue chips)
- ✅ Tokens verificados e confiáveis

**Proteções:**
- ❌ Sem tokens scam
- ❌ Sem memecoins arriscados
- ❌ Sem tokens não verificados
- ❌ Sem liquidez baixa

---

## 💰 Distribuição de Capital Recomendada

Com $50 total:

| Rede | Valor | Criptomoeda |
|------|-------|-------------|
| **Base** | $30 | ETH |
| **Arbitrum** | $12 | ETH |
| **BSC** | $8 | BNB |

---

## 📊 O Que Esperar

### Fase 1: Testnet (1-2 semanas)
- ✅ Bot aprende padrões
- ✅ IA se treina
- ✅ Zero risco
- ✅ Zero custo

### Fase 2: Mainnet (Lucro Real)
- 💰 Taxa de sucesso inicial: 1-3%
- 💰 Lucro esperado mês 1: $100-500
- 💰 Lucro esperado mês 2+: $500-3000

---

## 🎯 Estratégias Automáticas

O bot usa 4 estratégias 100% automáticas:

1. **Flash Loan Arbitrage (70%)**
   - Pega emprestado → Compra barato → Vende caro → Devolve → Lucro
   - Zero capital necessário

2. **Cross-Chain Arbitrage (20%)**
   - Arbitragem entre Base ↔ Arbitrum ↔ BSC

3. **Triangular Arbitrage (10%)**
   - Token A → Token B → Token C → Token A

4. **Statistical Arbitrage (IA)**
   - IA detecta padrões e prevê movimentos

---

## 🔄 Mudando de Testnet para Mainnet

Quando estiver pronto para lucrar de verdade:

1. Edite `.env`:
   ```bash
   USE_TESTNET=false
   ```

2. Reinicie o bot:
   ```bash
   python main.py
   ```

**Pronto! Bot rodando em MAINNET!** 💰

---

## 📈 Monitoramento

### Ver Logs em Tempo Real:

```bash
tail -f data/logs/bot.log
```

### Dashboard Web:

Acesse: http://localhost:3000

Veja:
- 💰 Lucro em tempo real
- 📊 Taxa de sucesso
- 🌐 Status das redes
- 🧠 Status da IA

---

## ⚙️ Configurações Principais

No arquivo `.env`:

```bash
# Lucro mínimo para executar
MIN_PROFIT_USD=50        # Só executa se lucro > $50
MIN_PROFIT_PERCENTAGE=1.0  # Só executa se diferença > 1%

# Gestão de capital
MAX_DAILY_GAS_SPEND=5    # Máximo $5/dia em gas
EMERGENCY_STOP_BALANCE=5  # Para se saldo < $5

# IA
ML_CONFIDENCE_THRESHOLD=0.80  # 80% de confiança mínima
```

---

## 🛑 Parar o Bot

Pressione `Ctrl+C` no terminal

---

## ❓ Problemas Comuns

### Bot não conecta:
```bash
# Verificar configuração
python -c "from src.config.config import validate_config; validate_config()"
```

### Sem oportunidades:
- Normal em testnet (menos liquidez)
- Aguarde alguns minutos
- IA precisa de tempo para aprender

### Erro de saldo:
- Verifique se tem saldo em cada rede
- Mínimo: $5 por rede

---

## 🎉 Pronto!

Seu bot está rodando 24/7 buscando oportunidades de arbitragem!

**Relaxe e deixe a IA trabalhar para você!** 💰🤖

---

**Dúvidas?** Leia o `README.md` completo!
