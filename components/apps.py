import tkinter as tk
from tkinter import ttk
from .ticker import CryptoTicker


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


class ToggleableTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard with Toggle")
        self.root.geometry("1000x400")

        # Control panel
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(fill=tk.X)

        self.sol_btn = ttk.Button(
            control_frame,
            text="Show SOL/USDT",
            command=self.toggle_sol
        )
        self.sol_btn.pack()

        # Ticker panel
        self.ticker_frame = ttk.Frame(root, padding=20)
        self.ticker_frame.pack(fill=tk.BOTH, expand=True)

        # Create tickers
        self.btc_ticker = CryptoTicker(
            self.ticker_frame, "btcusdt", "BTC/USDT")
        self.btc_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        self.eth_ticker = CryptoTicker(
            self.ticker_frame, "ethusdt", "ETH/USDT")
        self.eth_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        self.sol_ticker = CryptoTicker(
            self.ticker_frame, "solusdt", "SOL/USDT")
        # Don't pack SOL initially (hidden)

        # Start BTC and ETH
        self.btc_ticker.start()
        self.eth_ticker.start()

        self.sol_visible = False

    def toggle_sol(self):
        """Show or hide SOL ticker."""
        if self.sol_visible:
            # Hide SOL
            self.sol_ticker.stop()
            self.sol_ticker.pack_forget()
            self.sol_btn.config(text="Show SOL/USDT")
            self.sol_visible = False
        else:
            # Show SOL
            self.sol_ticker.pack(side=tk.LEFT, padx=10,
                                 fill=tk.BOTH, expand=True)
            self.sol_ticker.start()
            self.sol_btn.config(text="Hide SOL/USDT")
            self.sol_visible = True

    def on_closing(self):
        """Clean up when closing."""
        self.btc_ticker.stop()
        self.eth_ticker.stop()
        self.sol_ticker.stop()
        self.root.destroy()
