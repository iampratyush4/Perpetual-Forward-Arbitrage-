# 🔄 Perpetual Futures Arbitrage Bot

A Python-based bot to detect and exploit price discrepancies between spot and perpetual futures markets on Binance and other exchanges. Built for quantitative trading strategies.

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Testing-yellow)

---

## 📝 Table of Contents
- [Project Overview](#-project-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 🚀 Project Overview
This bot monitors real-time price differences between spot markets and perpetual futures contracts. It identifies arbitrage opportunities while accounting for funding rates and transaction costs. Designed for:
- **Quantitative traders** testing arbitrage strategies
- **Developers** learning algorithmic trading systems
- **Researchers** studying crypto market inefficiencies

---

## ✨ Features
| Feature | Description |
|---------|-------------|
| **Multi-Exchange Support** | Binance, Bybit, and FTX integration (extendable to others) |
| **Real-Time Monitoring** | Tracks spot/futures prices and funding rates every 60 seconds |
| **Risk Management** | Kelly Criterion position sizing and stop-loss thresholds |
| **Database Backend** | TimescaleDB for storing historical price data |
| **Paper Trading** | Test strategies risk-free with Binance Testnet |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Docker (for TimescaleDB)
- Binance/FTX API Keys (Testnet or Live)

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/your-project-name.git
   cd your-project-name
