# MEV-Bot with Flash Loan Arbitrage and Adaptive AI

A sophisticated bot for cross-chain arbitrage using Flash Loans from Aave V3 with adaptive AI optimization across Base, Arbitrum, and BSC networks.

## ✨ Features

- **Flash Loan Arbitrage**: Leverage Aave V3 flash loans for capital-free arbitrage
- **Cross-Chain Support**: Operates on Base, Arbitrum, and BSC networks
- **Adaptive AI**: TensorFlow-based machine learning that learns and optimizes strategies in real-time
- **Multi-DEX Integration**: Supports Uniswap V3, PancakeSwap, Aerodrome, and Camelot
- **Web Dashboard**: Real-time monitoring and analytics
- **Risk Management**: Circuit breakers and daily loss limits
- **Dry Run Mode**: Test strategies without executing real transactions

## 🛠️ Technologies

- **Python 3.11+**: Main programming language
- **Web3.py**: Ethereum blockchain interaction
- **Solidity**: Smart contract development
- **TensorFlow**: Machine learning for strategy optimization
- **Alchemy API**: RPC provider for blockchain access
- **FastAPI**: Web dashboard backend
- **React**: Web dashboard frontend

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 16+ (for dashboard)
- 50 USD in crypto for gas fees (distributed across networks)
- Alchemy API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/lucasandre16112000-png/06-mev-bot.git
cd 06-mev-bot
```

2. Create Python virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🚀 Running the Bot

### Start the Bot
```bash
python main.py
```

### Start the Dashboard
```bash
cd mev-dashboard
pnpm install
pnpm dev
```

Access dashboard at `http://localhost:3000`

## 🎯 How It Works

1. **Testnet Mode**: Bot learns on testnet without spending real money
2. **Opportunity Detection**: Monitors DEXs for arbitrage opportunities
3. **AI Optimization**: Machine learning adapts strategies based on market conditions
4. **Execution**: Executes profitable trades with flash loans
5. **Risk Management**: Enforces daily loss limits and gas spending caps

## 📊 Supported Networks

| Network | Status | Capital Required |
|---------|--------|------------------|
| Base    | ✅ Active | 60% of budget |
| Arbitrum| ✅ Active | 25% of budget |
| BSC     | ✅ Active | 15% of budget |

## 🔒 Security

- Testnet mode for safe testing
- Dry run mode to simulate trades
- Daily loss limits
- Circuit breaker protection
- Comprehensive logging

## 📝 Configuration

Edit `src/config/config.py` to customize:
- Network selection
- Risk parameters
- Trading strategies
- API endpoints

## 🏗️ Project Structure

```
.
├── src/
│   ├── core/          # Blockchain interaction
│   ├── strategies/    # Trading strategies
│   ├── ai/           # ML engine
│   └── utils/        # Utilities
├── mev-dashboard/    # Web dashboard
├── main.py          # Entry point
└── requirements.txt # Dependencies
```

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Lucas André - [GitHub](https://github.com/lucasandre16112000-png)

## ⚠️ Disclaimer

This bot is for educational purposes. Use at your own risk. Always test thoroughly on testnet before mainnet deployment.
