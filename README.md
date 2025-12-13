# Crypto Dashboard

A real-time cryptocurrency dashboard built with Python and Tkinter. Displays live market data from Binance, including price tickers, volume, order book, recent trades, and candlestick charts. Supports multiple cryptocurrencies with toggleable panels and saved preferences.

## Features

### Core Features

- Real-time price tracking for multiple cryptocurrencies (BTC, ETH, SOL, BNB, XRP, USDC)
- Color-coded price changes (green for positive, red for negative)
- 24-hour price change display
- Clean, organized, professional GUI
- Toggle buttons to show/hide panels
- Responsive layout that adapts to window resizing
- Persistent settings (last selected symbol and panel visibility)

### Advanced Features

- 24-hour volume display
- Order book showing top 10 bids and asks
- Recent trades feed
- Candlestick chart with volume using Matplotlib
- Multiple panels displaying different market information
- Efficient use of screen space

## Installation

### Requirements

- Python 3.7+

- Dependencies (install via pip):

```
pip install -r requirements.txt
```

### Clone the Repository

```
git clone https://github.com/CYRTRUS/cryptocurrency.git
cd cryptocurrency
```

## Usage

### Run the main application:

```
python main.py
```

- Click cryptocurrency buttons to switch Crypto.

- Toggle OrderBook or Chart panels using the yellow buttons.

- Settings are automatically saved on exit.

## Project Structure

```bash
crypto_dashboard/
├── main.py             # Entry point, main dashboard
├── media/              # Entry point, main dashboard
│ └── ui_design_01.png  # Figma UI Design
├── lib/                # Panels and utilities
│ ├── **init**.py
│ ├── ticker.py         # CryptoTicker panel
│ ├── volume.py         # 24h Volume panel
│ ├── orderbook.py      # OrderBookPanel
│ ├── last_trade.py     # LastTradePanel
│ ├── chart.py          # Candlestick chart panel
│ ├── debug.py          # Logging utility
│ ├── base_panel.py     # Base panel for Tkinter panels
│ └── base.py           # Base panel for WebSocket panels
├── requirements.txt    # All required dependencies
└── README.md           # This file
```

## The First Figma UI Design

![My Figama UI Design](media/ui_design_01.png)
