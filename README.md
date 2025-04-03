
# Perpetual Futures Arbitrage Bot

This project is a Python-based arbitrage bot designed to detect and capitalize on price discrepancies between spot and perpetual futures markets—primarily on Binance. It supports real-time monitoring, risk management, and is configurable for custom strategies. This tool is ideal for algorithmic traders, developers, and researchers studying market inefficiencies.

## 📌 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgements](#acknowledgements)

---

## 📈 Project Overview

The Perpetual Futures Arbitrage Bot continuously monitors real-time price differences between spot and perpetual futures markets to identify profitable arbitrage opportunities. It factors in transaction costs and funding rates to ensure trades are viable. It can be used for:

- Quantitative trading strategies and testing
- Learning algorithmic/automated trading systems
- Research on crypto market inefficiencies

---

## 🚀 Features

- **Real-Time Monitoring**: Continuously fetches and compares prices between spot and futures markets.
- **Arbitrage Detection**: Alerts or logs arbitrage windows when price differences exceed thresholds.
- **Risk Management**: Considers funding rates, slippage, and transaction fees before signaling.
- **Modular Design**: Easy to customize for new strategies or exchanges.
- **Configurable Parameters**: Easily change symbols, thresholds, and trade sizes.

---

## 🔧 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/iampratyush4/Perpetual-Forward-Arbitrage-.git
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd Perpetual-Forward-Arbitrage-
   ```

3. **Install Required Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

Before running the bot, set up the following:

1. **API Keys**

   Create a `.env` file in the root directory and add your Binance credentials:

   ```env
   API_KEY=your_api_key_here
   API_SECRET=your_api_secret_here
   ```

2. **Edit Trading Parameters**

   Open `config.py` and modify:

   ```python
   TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT']
   PRICE_DIFFERENCE_THRESHOLD = 0.5  # In percent
   ```

---

## 🧠 Usage

Run the bot with:

```bash
python main.py
```

The script will begin scanning for arbitrage opportunities based on the configurations you've set. Logs or alerts will notify you of any significant trades detected.

---

## 📁 Project Structure

```
├── .env                      # Contains API keys (not committed to Git)
├── README.md                 # Project documentation
├── config.py                 # Customizable bot parameters
├── database.py               # (Optional) Logging trade data
├── main.py                   # Main bot script
├── risk_engine.py            # Evaluates trade viability
├── requirements.txt          # Python dependencies
```

---

## 🤝 Contributing

Want to make this better? Awesome!

1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature-yourfeature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature-yourfeature
   ```
5. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License. See `LICENSE` for more details.

---

## 🙏 Acknowledgements

Special thanks to the open-source community and Binance’s robust API infrastructure that made this project possible. Also, shoutout to developers exploring the edge of crypto market efficiency!
```

---

