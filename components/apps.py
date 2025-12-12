import tkinter as tk
from tkinter import ttk
from .ticker import CryptoTicker
import requests


def fetch_initial_data(symbol):
    """Fetch initial price data for a symbol."""
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol.upper()}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            'price': float(data['lastPrice']),
            'change': float(data['priceChange']),
            'percent': float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error fetching initial data for {symbol}: {e}")
        return None


class BaseCryptoApp:
    """Base class for crypto dashboard apps."""

    def __init__(self, root, title="Crypto Dashboard"):
        self.root = root
        self.root.title(title)
        self.tickers = []

    def create_ticker(self, parent, symbol, display_name, show_immediately=True):
        """Create and connect a ticker with consistent initialization."""
        initial_data = fetch_initial_data(symbol)
        ticker = CryptoTicker(parent, symbol, display_name, initial_data)

        if show_immediately:
            ticker.show()
        else:
            ticker.hide()

        ticker.connect()
        self.tickers.append(ticker)
        return ticker

    def on_closing(self):
        """Clean up all tickers when closing."""
        for ticker in self.tickers:
            ticker.disconnect()
        self.root.destroy()


class MultiTickerApp(BaseCryptoApp):
    """Simple multi-ticker dashboard."""

    def __init__(self, root):
        super().__init__(root, "Crypto Dashboard")
        self.root.geometry("800x300")

        # Create ticker panel
        ticker_frame = ttk.Frame(root, padding=20)
        ticker_frame.pack(fill=tk.BOTH, expand=True)

        # Create BTC and ETH tickers
        self.btc_ticker = self.create_ticker(
            ticker_frame, "btcusdt", "BTC/USDT")
        self.eth_ticker = self.create_ticker(
            ticker_frame, "ethusdt", "ETH/USDT")


class ToggleableTickerApp(BaseCryptoApp):
    """Dashboard with toggleable tickers."""

    def __init__(self, root):
        super().__init__(root, "Crypto Dashboard with Toggle")
        self.root.geometry("1200x600")

        # Control panel
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(fill=tk.X)

        # Use tk.Button for color control
        self.sol_btn = tk.Button(
            control_frame,
            text="SOL/USDT",
            command=self.toggle_sol,
            font=("Arial", 10),
            padx=15,
            pady=5,
            bg="#A0A0A0",  # Gray when hidden
            fg="black",
            activebackground="#424242",
            activeforeground="black",
            relief="raised",
            cursor="hand2"
        )
        self.sol_btn.pack()

        # Ticker panel
        self.ticker_frame = ttk.Frame(root, padding=20)
        self.ticker_frame.pack(fill=tk.BOTH, expand=True)

        # Create all tickers with consistent initialization
        self.btc_ticker = self.create_ticker(
            self.ticker_frame, "btcusdt", "BTC/USDT")
        self.eth_ticker = self.create_ticker(
            self.ticker_frame, "ethusdt", "ETH/USDT")
        self.sol_ticker = self.create_ticker(
            self.ticker_frame, "solusdt", "SOL/USDT", show_immediately=False)

        # Track visibility state
        self.sol_visible = False

    def toggle_sol(self):
        """Show or hide SOL ticker UI (without stopping WebSocket)."""
        if self.sol_visible:
            # Hide SOL UI only
            self.sol_ticker.hide()
            self.sol_btn.config(
                bg="#A0A0A0",  # Gray when hidden
                fg="black",
                activebackground="#424242",
                activeforeground="black"
            )
            self.sol_visible = False
        else:
            # Show SOL UI only (WebSocket is already connected)
            self.sol_ticker.show()
            self.sol_btn.config(
                bg="#FFFFFF",  # White when shown
                fg="black",
                activebackground="#F5F5F5",
                activeforeground="black"
            )
            self.sol_visible = True
