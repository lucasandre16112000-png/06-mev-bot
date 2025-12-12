# 📋 O QUE VOCÊ PRECISA ME PASSAR

## ✅ OBRIGATÓRIO (para o bot funcionar):

### 1. APIs RPC (GRÁTIS)

Você precisa criar contas grátis e pegar as API keys:

**Opção A - Alchemy (Recomendado):**
- Site: https://www.alchemy.com
- Criar conta grátis
- Criar 3 apps:
  - Base (Mainnet ou Testnet)
  - Arbitrum (Mainnet ou Testnet)
  - Polygon (Mainnet ou Testnet)
- Copiar as URLs que vão ser tipo:
  - `https://base-mainnet.g.alchemy.com/v2/SEU_API_KEY_AQUI`
  - `https://arb-mainnet.g.alchemy.com/v2/SEU_API_KEY_AQUI`
  - `https://polygon-mainnet.g.alchemy.com/v2/SEU_API_KEY_AQUI`

**OU Opção B - Infura:**
- Site: https://infura.io
- Mesmo processo

**Me passe:**
- ✅ URL RPC da Base
- ✅ URL RPC do Arbitrum
- ✅ URL RPC do Polygon

---

### 2. Private Key da sua carteira

**ATENÇÃO:** Você NÃO vai me mandar! Vai ficar só no seu PC!

Mas preciso que você:
- ✅ Tenha a private key da sua MetaMask
- ✅ Saiba como pegar (expliquei no guia anterior)

Vou criar um arquivo `.env.example` e você só vai copiar e colar lá no seu PC.

---

## ⚙️ PREFERÊNCIAS (configurações do bot):

### 3. Parâmetros de operação

**Essas são as configurações que você pode ajustar:**

#### A) Lucro mínimo para executar trade:
- **Pergunta:** Qual o lucro mínimo em USD para o bot executar?
- **Recomendado:** $50 (para valer a pena o gas)
- **Você quer:** $____?

#### B) Lucro mínimo em porcentagem:
- **Pergunta:** Qual a diferença de preço mínima para executar?
- **Recomendado:** 1% (mais seguro)
- **Você quer:** ____%?

#### C) Gasto máximo de gas por dia:
- **Pergunta:** Quanto você quer gastar no máximo por dia em tentativas?
- **Recomendado:** $5/dia (para não queimar seu capital rápido)
- **Você quer:** $____/dia?

#### D) Saldo de emergência:
- **Pergunta:** Quando o bot deve parar automaticamente?
- **Recomendado:** Quando saldo < $5 (para não gastar tudo)
- **Você quer:** $____?

---

## 🤔 SOBRE SUA DÚVIDA: "QUANTOS DÓLARES PARA TRADER"

### Deixa eu explicar:

Você tem **$50 TOTAL** para distribuir entre as 3 redes, certo?

**Exemplo de distribuição:**
- Base: $30 em ETH (60% de prioridade)
- Arbitrum: $12 em ETH (25% de prioridade)
- Polygon: $8 em MATIC (15% de prioridade)

### MAS ATENÇÃO: Esses $50 são APENAS para pagar GAS!

**Você NÃO usa esses $50 para comprar tokens!**

### Como funciona na prática:

**Flash Loan Arbitrage:**
1. Bot detecta: ETH custa $2000 na Uniswap, $2020 na Aerodrome
2. Bot pega emprestado $100.000 (flash loan)
3. Compra ETH por $100k
4. Vende ETH por $102k
5. Devolve $100k + taxa
6. Lucro: $2k
7. **Gas pago:** $0.01 (dos seus $30 de ETH na Base)

**Você NÃO usou seus $30 para comprar! Usou só $0.01 de gas!**

### Então por que perguntei sobre "quanto quer usar por trade"?

**Eu estava confuso! 😅**

Na verdade, com **Flash Loans você NÃO precisa definir quanto usar por trade**, porque:
- O bot pega emprestado automaticamente
- Quanto mais diferença de preço, mais ele pega emprestado
- Você só paga o gas (fixo: $0.01-0.50)

### O que você REALMENTE precisa definir:

**Apenas o lucro mínimo para executar:**
- Se você colocar $50 mínimo, o bot só executa se lucro > $50
- Se você colocar $100 mínimo, o bot só executa se lucro > $100

**Recomendação:** $50 mínimo (para valer a pena)

---

## 📊 RESUMO DO QUE PRECISO:

### OBRIGATÓRIO:
1. ✅ URL RPC Base (Alchemy ou Infura)
2. ✅ URL RPC Arbitrum (Alchemy ou Infura)
3. ✅ URL RPC Polygon (Alchemy ou Infura)

### PREFERÊNCIAS (ou uso valores recomendados):
1. Lucro mínimo: $____ (recomendado: $50)
2. Lucro mínimo %: ____% (recomendado: 1%)
3. Gasto máximo gas/dia: $____ (recomendado: $5)
4. Saldo de emergência: $____ (recomendado: $5)

### NÃO PRECISO:
- ❌ Private key (fica só no seu PC)
- ❌ Quanto quer usar por trade (não se aplica a flash loans)
- ❌ API CoinMarketCap (não vou usar)

---

## 🚀 DEPOIS QUE VOCÊ ME PASSAR:

Vou criar:
1. ✅ Arquivo `.env.example` com todas as configurações
2. ✅ Bot completo e funcional
3. ✅ Dashboard web
4. ✅ Documentação de como rodar
5. ✅ Scripts de instalação

Você vai só:
1. Copiar `.env.example` para `.env`
2. Colar suas URLs RPC
3. Colar sua private key
4. Rodar 1 comando: `python main.py`

---

## ❓ ESTÁ CLARO AGORA?

**Resumindo:**
- Seus $50 são APENAS para gas
- Flash Loan pega emprestado automaticamente
- Você só define o lucro MÍNIMO para executar
- Não precisa definir "quanto usar por trade"

**Me mande:**
1. As 3 URLs RPC (Alchemy/Infura)
2. Suas preferências de lucro mínimo (ou uso os recomendados)

**Pronto! Só isso que preciso!** 🎯
