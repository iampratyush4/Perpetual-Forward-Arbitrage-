# Perpetual Futures Arbitrage Bot

A Python‐based arbitrage bot that monitors price discrepancies between spot and perpetual futures markets on Binance, calculates risk‐adjusted position sizes via the Kelly Criterion, and executes hedged trades when profitable opportunities arise. This README will walk you through a step‐by‐step process to clone, configure, and run the project locally.

---

## Table of Contents

- [Perpetual Futures Arbitrage Bot](#perpetual-futures-arbitrage-bot)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up a Python Virtual Environment](#set-up-a-python-virtual-environment)
  - [Install Dependencies](#install-dependencies)
  - [Create and Populate the `.env` File](#create-and-populate-the-env-file)
  - [Review and Adjust `config.py`](#review-and-adjust-configpy)
  - [(Optional) Database Initialization](#optional-database-initialization)
  - [Run the Bot](#run-the-bot)
  - [Directory Structure Explained](#directory-structure-explained)
  - [Logging \& Outputs](#logging--outputs)
  - [Common Troubleshooting](#common-troubleshooting)
  - [Customizing the Strategy](#customizing-the-strategy)
  - [Contributing](#contributing)
  - [License](#license)
  - [Final Notes](#final-notes)

---

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:

* **Operating System**: Windows 10+, macOS 10.13+, or any modern Linux distribution
* **Python**: ≥ 3.8 (ideally 3.9 or 3.10)
* **Git**: Latest stable release (for cloning and updating the repository)
* **Binance Account**: Create API keys (API key + API secret) with “Enable Spot Trading” and “Enable Futures Trading” permissions.

> **Note**: Always keep your API keys secure. Do not share them publicly or commit them into version control.

---

## Clone the Repository

1. Open a terminal or command prompt.

2. Navigate to the directory where you want to store this project (e.g., `~/projects/`).

3. Clone the GitHub repository:

   ```bash
   git clone https://github.com/iampratyush4/Perpetual-Forward-Arbitrage-.git
   ```

4. Change into the cloned project directory:

   ```bash
   cd Perpetual-Forward-Arbitrage-
   ```

   At this point, you should see:

   ```
   .
   ├── .env
   ├── README.md
   ├── config.py
   ├── database.py
   ├── main.py
   ├── risk_engine.py
   ├── requirements.txt
   └── ...
   ```

---

## Set Up a Python Virtual Environment

It is highly recommended to run this project inside a virtual environment to isolate dependencies.

1. From the project root directory, create a virtual environment (using `venv`):

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:

   * **macOS / Linux**:

     ```bash
     source venv/bin/activate
     ```

   * **Windows (PowerShell)**:

     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

   * **Windows (CMD)**:

     ```cmd
     .\venv\Scripts\activate.bat
     ```

3. After activation, your prompt should be prefixed with `(venv)`.

---

## Install Dependencies

With the virtual environment activated, install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **requirements.txt** typically includes (but is not limited to):
>
> * `python-binance` (wrapper for Binance Spot & Futures API)
> * `python-dotenv` (to load environment variables from `.env`)
> * `pandas`, `numpy` (for data handling and calculations)
> * `websockets`, `requests` (if used in the code)
> * Any other dependencies listed in `requirements.txt`

You should see something like:

```
Collecting python-binance
  Downloading python_binance-1.x.x-py3-none-any.whl (xxx kB)
Collecting python-dotenv
  Downloading python_dotenv-0.x.x.tar.gz (xx kB)
...
Successfully installed python-binance python-dotenv pandas numpy ...
```

---

## Create and Populate the `.env` File

1. In the project root, there is a sample file named `.env`. If it does not exist, create a new file called `.env` (no extension).

2. Open `.env` in your preferred text editor and add your Binance API credentials:

   ```dotenv
   API_KEY=your_binance_api_key_here
   API_SECRET=your_binance_api_secret_here
   ```

   * **Important**: Do **not** include quotes around the key or secret.
   * **Example**:

     ```dotenv
     API_KEY=abc123def456ghi789jkl
     API_SECRET=0123456789abcdefghijklmnopqrstuv
     ```

3. Save and close `.env`.

4. Verify that `.env` is in `.gitignore` to prevent accidental commits of sensitive credentials.

---

## Review and Adjust `config.py`

The `config.py` file contains all customizable parameters of the bot:

```python
# Example contents of config.py

# 1. TRADING_PAIRS: list of symbols to monitor (spot vs perpetual futures)
TRADING_PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    # add more pairs as desired
]

# 2. PRICE_DIFFERENCE_THRESHOLD: percentage difference between spot and futures prices
#    before triggering an arbitrage signal (e.g., 0.5 means 0.5% difference)
PRICE_DIFFERENCE_THRESHOLD = 0.5

# 3. ORDER_SIZE_USDT: capital in USDT allocated per leg of each arbitrage trade
ORDER_SIZE_USDT = 100.0

# 4. MAX_LEVERAGE: maximum leverage to use on the futures side (e.g., 5x, 10x)
MAX_LEVERAGE = 10

# 5. FUNDING_RATE_BUFFER: a cushion (in decimals) to ensure funding fees don’t wipe out profits
#    (e.g., 0.0005 = 0.05%)
FUNDING_RATE_BUFFER = 0.0005

# 6. STOP_LOSS_PERCENT: if the market moves against the hedged position by X%, close position
STOP_LOSS_PERCENT = 1.0

# 7. DATABASE_FILENAME: name of the SQLite database file for logging (optional)
DATABASE_FILENAME = "arbitrage_trades.db"
```

1. **Open `config.py`** in your editor.

2. Modify the following sections to suit your strategy and risk tolerance:

   * **Trading Pairs**
     Add or remove symbols from `TRADING_PAIRS = [ ... ]`. For example, if you want to watch `BNBUSDT`, simply append `"BNBUSDT"` to the list.

   * **Price Difference Threshold**
     The bot will only consider an arbitrage opportunity if

     $$
       \bigg|\frac{FuturesPrice - SpotPrice}{SpotPrice}\bigg| \times 100 \;\;\text{(in percent)}\;\; \geq\; PRICE_DIFFERENCE_THRESHOLD
     $$

     A lower threshold means more sensitive signals—but higher risk of false positives. A higher threshold might miss smaller windows.

   * **Order Size (USDT)**
     Each detected opportunity results in:

     1. Buying (or selling) `ORDER_SIZE_USDT` worth of the spot asset.
     2. Simultaneously opening an opposite futures position with comparable notional value.

     Adjust to the capital you want to allocate per pair.

   * **Leverage & Funding Rate Buffer**

     * `MAX_LEVERAGE`: How much leverage to use on the futures leg.
     * `FUNDING_RATE_BUFFER`: A “safety margin” added/subtracted from the current funding rate to avoid negative‐funding‐rate traps.

   * **Stop Loss**
     A fail‐safe: if your hedged position (spot + futures) loses more than `STOP_LOSS_PERCENT`, the bot will attempt to close both legs to avoid runaway losses.
     – If you prefer to handle risk manually, you can set `STOP_LOSS_PERCENT = None` (but be careful).

   * **Database Logging** (Optional)
     If you want to record every trade to SQLite, set `DATABASE_FILENAME` to something like `"my_trades.db"`.
     Leave as `None` or `""` if you do not wish to log.

3. Save and close `config.py`.

---

## (Optional) Database Initialization

By default, the bot can log each executed arbitrage trade (timestamp, pair, direction, P\&L, funding rate, etc.) into a local SQLite database.

1. If you have left `DATABASE_FILENAME = "arbitrage_trades.db"` (or any filename) in `config.py`, the first time you run `main.py`, the code in `database.py` will automatically create the database and necessary tables.

2. If you want to inspect the SQLite file manually, you can use any SQLite client (e.g., `sqlite3` CLI on Linux/macOS or [DB Browser for SQLite](https://sqlitebrowser.org/) on Windows).

   ```bash
   sqlite3 arbitrage_trades.db
   sqlite> .tables
   trades
   sqlite> SELECT * FROM trades LIMIT 5;
   ```

3. If you do **not** want to store anything, simply edit `config.py` and set:

   ```python
   DATABASE_FILENAME = ""
   ```

   Then the database code will skip any writes.

---

## Run the Bot

With the virtual environment activated, dependencies installed, and configuration set:

1. Ensure your working directory is still the project root (where `main.py` resides).

2. Run the main script:

   ```bash
   python main.py
   ```

3. **What to expect**:

   * The bot will load environment variables (your API keys) via `python-dotenv`.

   * It will read `config.py` to fetch trading pairs, thresholds, and other parameters.

   * It will connect to Binance Spot and Futures endpoints via the `python-binance` library.

   * It will fetch real‐time prices (every few seconds) for each symbol in `TRADING_PAIRS`:

     * Spot price → `client.get_symbol_ticker(symbol="BTCUSDT")`
     * Futures price → `client.futures_symbol_ticker(symbol="BTCUSDT")`
     * Current funding rate → `client.futures_funding_rate(...)`

   * It calculates the percent difference:

     $$
       \Delta \%= \Big|\frac{Futures - Spot}{Spot}\Big|\times 100
     $$

   * If `Δ% ≥ PRICE_DIFFERENCE_THRESHOLD`, it runs through `risk_engine.py` to:

     1. Check the current funding rate against `FUNDING_RATE_BUFFER`.
     2. Compute position sizes via the Kelly Criterion (to maximize growth while controlling risk).
     3. Compare that against `ORDER_SIZE_USDT` and `MAX_LEVERAGE`.
     4. If all checks pass, it sends simultaneous orders:

        * **Spot**: `client.order_market_buy(...)` or `client.order_market_sell(...)` depending on arbitrage direction.
        * **Futures**: `client.futures_create_order(...)` with leverage set by `client.futures_change_leverage(...)`.
     5. Logs trade details into SQLite (if configured).

4. **Stopping the Bot**

   * Press `Ctrl+C` to interrupt.
   * The script will attempt to gracefully close any open positions if it can detect them before exit.
   * Check the logs in your console (or the SQLite DB) to confirm the last action.

---

## Directory Structure Explained

```
Perpetual-Forward-Arbitrage-/
├── .env                   # Your local environment variables (API keys); *do not* commit.
├── README.md              # This documentation.
├── config.py              # User‐editable parameters (symbols, thresholds, order sizes).
├── database.py            # Module to initialize/write to SQLite (optional).
├── main.py                # Entry point: ties together data fetching, signal generation, risk checks, and order execution.
├── risk_engine.py         # Contains functions for Kelly Criterion, funding‐rate checks, SL logic.
├── requirements.txt       # All Python dependencies (python-binance, python-dotenv, pandas, numpy, etc.).
└── LICENSE                # MIT License.
```

* **`.env`**
  Should only contain:

  ```
  API_KEY=...
  API_SECRET=...
  ```

  This file is loaded automatically by `python-dotenv` at runtime. Keep it private.

* **`config.py`**
  Edit this to:

  * Select which symbols to watch
  * Define thresholds, buffer zones, leverage, and order sizing.

* **`main.py`**
  Example structure (pseudocode):

  ```python
  from dotenv import load_dotenv
  import os
  from python_binance import Client
  from config import TRADING_PAIRS, PRICE_DIFFERENCE_THRESHOLD, ...
  from risk_engine import compute_kelly_position, should_trade, ...
  from database import DatabaseManager

  def main():
      load_dotenv()  # reads .env
      api_key = os.getenv("API_KEY")
      api_secret = os.getenv("API_SECRET")
      client = Client(api_key, api_secret)

      db = DatabaseManager(DATABASE_FILENAME) if DATABASE_FILENAME else None

      # Infinite loop for scanning prices
      while True:
          now = datetime.utcnow()
          for symbol in TRADING_PAIRS:
              spot_price = float(client.get_symbol_ticker(symbol=symbol)["price"])
              future_price = float(client.futures_symbol_ticker(symbol=symbol)["price"])
              diff_pct = abs((future_price - spot_price) / spot_price) * 100

              if diff_pct >= PRICE_DIFFERENCE_THRESHOLD:
                  # fetch funding rate, compute position sizes
                  position_size = compute_kelly_position(...)
                  if should_trade(...):
                      # Place spot + futures orders
                      spot_order = client.order_market_...
                      future_order = client.futures_create_order(...)
                      if db:
                          db.log_trade(...)
          sleep(POLL_INTERVAL_SECONDS)
  ```

* **`risk_engine.py`**
  Contains:

  * **Kelly Criterion**: estimate the optimal fraction of capital to risk given historical win rate / payoff ratio.
  * **Funding Rate Check**: ensure the next funding payment does not wipe out your profit.
  * **Stop-Loss Logic**: monitor open trades, close them if adverse movement exceeds `STOP_LOSS_PERCENT`.

* **`database.py`**
  If enabled, it:

  1. Creates an SQLite database (if not exists).
  2. Defines a `trades` table with columns like `(id, timestamp, symbol, side, order_size, entry_price, exit_price, pnl, funding_rate, ...)`.
  3. Provides a `log_trade()` function you call right after successful execution.

---

## Logging & Outputs

* **Console Output**
  The bot prints status messages, including:

  * Current UTC time.
  * For each scanned pair: spot & futures price, percent difference.
  * “Arbitrage detected for SYMBOL” when threshold is crossed.
  * Details of any order placed (quantity, executed price, fees).
  * Stop‐loss triggers (if any).

* **SQLite Database** (if enabled)

  * File name = `DATABASE_FILENAME` from `config.py`.
  * Table: `trades` with columns like:

    ```
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    symbol TEXT,
    side TEXT,
    spot_price REAL,
    future_price REAL,
    order_size_usdt REAL,
    funding_rate REAL,
    kelly_size REAL,
    swap_direction TEXT,  -- e.g., "Sell Spot / Long Future"
    exit_price REAL,
    pnl_usdt REAL
    ```
  * After each completed arbitrage cycle (entry + exit), a new row is inserted.

* **Log Rotation / Archiving**

  * By default, the bot does not rotate logs.
  * If you want to keep a perpetual log file, you can run:

    ```bash
    python main.py 2>&1 | tee -a arbitrage_bot.log
    ```

    Then manually rotate/cleanup `arbitrage_bot.log` as needed.

---

## Common Troubleshooting

1. **“Module Not Found” Errors**

   * Double‐check that your virtual environment is activated:

     ```bash
     which python
     which pip
     ```

     Both should point to the `venv/` folder.
   * Run:

     ```bash
     pip install -r requirements.txt
     ```

2. **“API Key/Secret Invalid” or “Binance Request 401 Unauthorized”**

   * Verify your `.env` file is in the same directory as `main.py`.
   * Ensure you have no extra spaces/trailing newlines in `.env` values.
   * Check on the Binance Dashboard that your API key is active, and that you have enabled spot/futures permissions.

3. **Rate Limiting / “HTTP 429 Too Many Requests”**

   * Binance enforces strict rate limits. If you see “429” or “418” errors:

     * Increase `POLL_INTERVAL_SECONDS` (in your code) so you fetch less frequently.
     * Consider using WebSocket streams for real‐time price updates instead of polling.
     * Add a short `sleep(0.5)` between consecutive API calls.

4. **Orders Not Filling / Insufficient Margin**

   * Verify you have enough USDT in your spot wallet for the spot leg.
   * Verify you have sufficient margin in your futures wallet.
   * If using high leverage, the required initial margin may be larger than expected.
   * Test on Binance Testnet (requires separate testnet API keys) before going live.

5. **SQLite “Database is Locked” Error**

   * This occurs if two processes try to write at the same time.
   * Ensure only one instance of the bot is running.
   * If you manually inspect the DB with a SQLite client while the bot is writing, you may get locks. Pause the bot first.

6. **“Funding Rate Too High / Negative” Causing Loss**

   * The `FUNDING_RATE_BUFFER` in `config.py` acts as a guardrail.
   * If you see that the next funding rate is negative (meaning you pay the funding fee instead of collecting), adjust `FUNDING_RATE_BUFFER` upward (e.g., from `0.0005` to `0.0010`) or skip trading that symbol entirely.

---

## Customizing the Strategy

1. **Adding New Symbols**

   * Edit `TRADING_PAIRS` in `config.py`:

     ```python
     TRADING_PAIRS = [
         "BTCUSDT",
         "ETHUSDT",
         "BNBUSDT",
         "SOLUSDT",      # newly added
         "ADAUSDT",      # newly added
     ]
     ```
   * Save and restart the bot. It will begin scanning those pairs immediately.

2. **Adjusting Thresholds**

   * If the market is very volatile, you might experience many false positives. Increase `PRICE_DIFFERENCE_THRESHOLD` (e.g., from `0.5` to `1.0`).
   * If you want earlier signals (more frequent, smaller windows), decrease it (e.g., from `0.5` to `0.25`).

3. **Switching to Limit Orders**

   * By default, `main.py` uses `order_market_buy()` and `futures_create_order(type='MARKET', ...)`.
   * To use limit orders, modify the code:

     ```python
     # SPOT LIMIT (e.g., buy at spot_price * 1.0005)
     limit_price = round(spot_price * 1.0005, 2)
     spot_order = client.create_order(
         symbol=symbol,
         side=Client.SIDE_BUY,
         type=Client.ORDER_TYPE_LIMIT,
         quantity=calculated_qty_spot,
         price=str(limit_price),
         timeInForce=Client.TIME_IN_FORCE_GTC
     )
     ```
   * Similarly, adjust your futures order to `type='LIMIT'` with an appropriate price.

4. **Backtesting Mode (No Live Orders)**

   * If you want to simulate the strategy without sending real orders:

     * In `main.py`, introduce a global flag at the top:

       ```python
       DRY_RUN = True  # Set to False to go live
       ```
     * Wrap actual order calls in:

       ```python
       if not DRY_RUN:
           # place orders on Binance
       else:
           # print simulated fill details
       ```
   * Collect timestamps, prices, and simulate P\&L to CSV for analysis.

---

## Contributing

Contributions are welcome! To propose changes or improvements:

1. Fork the repository:

   ```bash
   git clone https://github.com/your-username/Perpetual-Forward-Arbitrage-.git
   cd Perpetual-Forward-Arbitrage-
   ```

2. Create a new branch:

   ```bash
   git checkout -b feature/your-improvement
   ```

3. Make your changes, then stage & commit:

   ```bash
   git add .
   git commit -m "Add support for limit orders"
   ```

4. Push your branch to your fork:

   ```bash
   git push origin feature/your-improvement
   ```

5. Open a Pull Request against `iampratyush4/Perpetual-Forward-Arbitrage-` main branch. Provide:

   * A clear title and description of your changes.
   * Any testing steps you performed.
   * Rationale for why the change is useful (performance, new feature, bug fix).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Final Notes

* **Security**: Do not commit your `.env` file. Always keep API keys off public repositories.
* **Testing**: We strongly recommend experimenting on the [Binance Testnet](https://testnet.binance.vision/) before deploying on mainnet, especially if you are new to margin/futures trading.
* **Risk**: Arbitrage strategies can be profitable but carry risks—slippage, sudden funding‐rate swings, exchange downtime, API errors, and execution delays. Monitor your positions closely, especially when first going live.

Thank you for using the Perpetual Futures Arbitrage Bot. If you encounter any issues or have questions, feel free to open an issue on GitHub or reach out to the repository maintainer. Happy trading!
