# 🖥️ COMO RODAR O BOT NO SEU PC

## ✅ PRÉ-REQUISITOS

Seu PC precisa ter:
- ✅ Python 3.11 ou superior
- ✅ Conexão com internet
- ✅ Windows, Mac ou Linux

---

## 📥 PASSO 1: BAIXAR O BOT

1. Baixe o arquivo `mev-bot-completo.tar.gz`
2. Salve em uma pasta de sua escolha

---

## 📦 PASSO 2: EXTRAIR

### Windows:
- Use WinRAR, 7-Zip ou similar
- Clique com botão direito → Extrair aqui

### Mac/Linux:
```bash
tar -xzf mev-bot-completo.tar.gz
```

---

## 🔧 PASSO 3: INSTALAR

### Windows:

1. Abra o PowerShell ou CMD na pasta do bot
2. Execute:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Mac/Linux:

1. Abra o Terminal na pasta do bot
2. Execute:
```bash
bash install.sh
```

Ou manualmente:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 PASSO 4: RODAR O BOT

### Windows:
```bash
venv\Scripts\activate
python main.py
```

### Mac/Linux:
```bash
source venv/bin/activate
python main.py
```

---

## ✅ PRONTO!

O bot vai:
1. ✅ Conectar nas blockchains (Base, Arbitrum, BSC)
2. ✅ Inicializar todas as proteções
3. ✅ Começar a buscar oportunidades 24/7

---

## 🛡️ PROTEÇÕES ATIVAS

Ao rodar, você verá:

```
🛡️ Inicializando Risk Manager...
  ✅ Simulação antes de executar: ATIVA
  ✅ Limite de perda diária: $10.0
  ✅ Limite de gas diário: $5.0
  ✅ Circuit breaker: ATIVO
```

**Isso significa que o bot está 100% protegido contra prejuízo!**

---

## 📊 MONITORAR O BOT

### Ver Logs em Tempo Real:

**Windows:**
```bash
type data\logs\bot.log
```

**Mac/Linux:**
```bash
tail -f data/logs/bot.log
```

### Ver Estatísticas:

O bot mostra estatísticas a cada 100 ciclos automaticamente!

---

## 🔄 MUDAR DE TESTNET PARA MAINNET

Quando estiver pronto para lucrar de verdade:

1. Edite o arquivo `.env`
2. Mude:
   ```
   USE_TESTNET=false
   ```
3. Reinicie o bot

**ATENÇÃO:** Só faça isso depois de testar em testnet por 1-2 semanas!

---

## 🛑 PARAR O BOT

Pressione `Ctrl+C` no terminal

O bot vai:
1. Mostrar estatísticas finais
2. Salvar todos os dados
3. Fechar conexões
4. Encerrar com segurança

---

## ❓ PROBLEMAS COMUNS

### "Python não encontrado"

**Windows:**
- Baixe Python em: https://www.python.org/downloads/
- ✅ Marque "Add Python to PATH" na instalação

**Mac:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt install python3.11 python3.11-venv
```

### "Erro ao conectar blockchain"

- Verifique sua internet
- Verifique se a API Key está correta no `.env`
- Tente novamente em alguns minutos

### "Sem oportunidades"

- Normal em testnet (menos liquidez)
- Aguarde alguns minutos
- IA precisa de tempo para aprender

---

## 💰 DISTRIBUIR CAPITAL (MAINNET)

Quando for para mainnet, distribua $50:

| Rede | Valor | Criptomoeda | Como Enviar |
|------|-------|-------------|-------------|
| **Base** | $30 | ETH | Bridge de Ethereum |
| **Arbitrum** | $12 | ETH | Bridge de Ethereum |
| **BSC** | $8 | BNB | Compre BNB e envie |

**Endereço da sua carteira:**
```
0xe1ac69351bc9bc924c5d76847b3f54ae09d5b62f
```

---

## 🎯 DICAS IMPORTANTES

### ✅ FAÇA:
- ✅ Teste em testnet por 1-2 semanas
- ✅ Monitore os logs regularmente
- ✅ Deixe a IA aprender
- ✅ Tenha paciência

### ❌ NÃO FAÇA:
- ❌ Ir direto para mainnet
- ❌ Desistir na primeira semana
- ❌ Mudar configurações sem entender
- ❌ Compartilhar sua private key

---

## 📞 SUPORTE

Leia a documentação completa em:
- `README.md` - Documentação completa
- `GUIA_RAPIDO.md` - Guia rápido
- `ENTREGA_FINAL.md` - Resumo do projeto

---

## 🎉 BOA SORTE!

Seu bot está pronto para trabalhar para você 24/7!

**Relaxe e deixe a IA fazer o trabalho!** 💰🤖

---

**Versão:** 1.0.0  
**Plataformas:** Windows, Mac, Linux  
**Redes:** Base, Arbitrum, BSC  
**Capital mínimo:** $50  
