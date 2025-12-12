# 🤖 MEV-Bot com Arbitragem de Flash Loan e IA Adaptativa

Um bot sofisticado para arbitragem cross-chain usando Flash Loans da Aave V3 com otimização de IA adaptativa nas redes Base, Arbitrum e BSC.

## ✨ Funcionalidades

- **Arbitragem com Flash Loan**: Aproveita os flash loans da Aave V3 para arbitragem sem capital.
- **Suporte Cross-Chain**: Opera nas redes Base, Arbitrum e BSC.
- **IA Adaptativa**: Machine learning baseado em TensorFlow que aprende e otimiza estratégias em tempo real.
- **Integração Multi-DEX**: Suporta Uniswap V3, PancakeSwap, Aerodrome e Camelot.
- **Dashboard Web**: Monitoramento e análise em tempo real.

## 🛠️ Tecnologias

- **Python 3.11+**: Linguagem de programação principal.
- **Web3.py**: Interação com a blockchain Ethereum.
- **Solidity**: Desenvolvimento de smart contracts.
- **TensorFlow**: Machine learning para otimização de estratégias.
- **FastAPI**: Backend do dashboard web.
- **React**: Frontend do dashboard web.

## 📋 Guia de Instalação e Execução (Para Qualquer Pessoa)

### Pré-requisitos

1.  **Git**: [**Download aqui**](https://git-scm.com/downloads)
2.  **Python**: [**Download aqui**](https://www.python.org/downloads/) (versão 3.11+)
3.  **Node.js**: [**Download aqui**](https://nodejs.org/) (versão 16+)
4.  **Chave da Alchemy**: Crie uma conta gratuita na [Alchemy](https://www.alchemy.com/) para obter uma chave de API.

### Passo 1: Baixar o Projeto

```bash
git clone https://github.com/lucasandre16112000-png/06-mev-bot.git
cd 06-mev-bot
```

### Passo 2: Configurar o Ambiente Python

```bash
# No Windows
python -m venv venv
.\venv\Scripts\activate

# No macOS ou Linux
python3.11 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Passo 3: Configurar as Variáveis de Ambiente

Copie o arquivo de exemplo e preencha com suas informações:

```bash
cp .env.example .env
```

Agora, edite o arquivo `.env` e adicione sua chave da Alchemy e outras credenciais.

### Passo 4: Executar o Bot

```bash
python main.py
```

### Passo 5: (Opcional) Executar o Dashboard

Em um novo terminal:

```bash
cd mev-dashboard
pnpm install
pnpm dev
```

Acesse o dashboard em `http://localhost:3000`.

## 👨‍💻 Autor

Lucas André S - [GitHub](https://github.com/lucasandre16112000-png)
