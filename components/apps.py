import tkinter as tk
from tkinter import ttk
from .ticker import CryptoTicker
import requests
import threading


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


class ToggleableTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard with Toggle")
        self.root.geometry("1200x800")

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
            bg="#A0A0A0",
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

        # Create BTC ticker with initial data
        btc_data = fetch_initial_data("BTCUSDT")
        self.btc_ticker = CryptoTicker(
            self.ticker_frame, "btcusdt", "BTC/USDT", btc_data)
        self.btc_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        # Create ETH ticker with initial data
        eth_data = fetch_initial_data("ETHUSDT")
        self.eth_ticker = CryptoTicker(
            self.ticker_frame, "ethusdt", "ETH/USDT", eth_data)
        self.eth_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        # Create SOL ticker WITHOUT initial data initially
        self.sol_ticker = CryptoTicker(
            self.ticker_frame, "solusdt", "SOL/USDT")
        # Don't pack SOL initially (hidden)

        # Pre-fetch SOL data in background
        self.sol_initial_data = None

        def pre_fetch_and_update():
            """Pre-fetch SOL data and update the ticker if it exists."""
            data = fetch_initial_data("SOLUSDT")
            if data:
                self.sol_initial_data = data

                self.root.after(0, self.update_sol_display, data)
            else:
                print("✗ Failed to pre-fetch SOL data")

        # Start pre-fetching in background thread
        threading.Thread(target=pre_fetch_and_update, daemon=True).start()

        # Start BTC and ETH
        self.btc_ticker.start()
        self.eth_ticker.start()

        self.sol_visible = False

    def update_sol_display(self, data):
        """Update SOL ticker with pre-fetched data."""
        if hasattr(self, 'sol_ticker'):
            self.sol_ticker.update_display(
                data['price'],
                data['change'],
                data['percent']
            )

    def toggle_sol(self):
        """Show or hide SOL ticker."""
        if self.sol_visible:
            # Hide SOL
            self.sol_ticker.stop()
            self.sol_ticker.pack_forget()
            self.sol_btn.config(
                bg="#A0A0A0",
                fg="black",
                activebackground="#424242",
                activeforeground="black"
            )
            self.sol_visible = False
        else:
            # Show SOL - Update with latest data if available
            if self.sol_initial_data:
                # Use the pre-fetched data
                self.sol_ticker.update_display(
                    self.sol_initial_data['price'],
                    self.sol_initial_data['change'],
                    self.sol_initial_data['percent']
                )

            self.sol_ticker.pack(side=tk.LEFT, padx=10,
                                 fill=tk.BOTH, expand=True)
            self.sol_ticker.start()
            self.sol_btn.config(
                bg="#FFFFFF",
                fg="black",
                activebackground="#F5F5F5",
                activeforeground="black"
            )
            self.sol_visible = True

    def on_closing(self):
        """Clean up when closing."""
        self.btc_ticker.stop()
        self.eth_ticker.stop()
        self.sol_ticker.stop()
        self.root.destroy()


class MultiTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("800x300")

        # Create ticker panel
        ticker_frame = ttk.Frame(root, padding=20)
        ticker_frame.pack(fill=tk.BOTH, expand=True)

        # Create BTC ticker
        self.btc_ticker = CryptoTicker(ticker_frame, "btcusdt", "BTC/USDT")
        self.btc_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        # Create ETH ticker
        self.eth_ticker = CryptoTicker(ticker_frame, "ethusdt", "ETH/USDT")
        self.eth_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        # Start both tickers
        self.btc_ticker.start()
        self.eth_ticker.start()

    def on_closing(self):
        """Clean up when closing."""
        self.btc_ticker.stop()
        self.eth_ticker.stop()
        self.root.destroy()
