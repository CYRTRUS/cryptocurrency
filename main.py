import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading


class CryptoTicker:
    """Reusable ticker component for any cryptocurrency."""

    def __init__(self, parent, symbol, display_name):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.is_active = False
        self.ws = None

        # Create UI
        self.frame = ttk.Frame(parent, relief="solid",
                               borderwidth=1, padding=20)

        # Title
        ttk.Label(self.frame, text=display_name,
                  font=("Arial", 16, "bold")).pack()

        # Price
        self.price_label = tk.Label(self.frame, text="--,---",
                                    font=("Arial", 40, "bold"))
        self.price_label.pack(pady=10)

        # Change
        self.change_label = tk.Label(self.frame, text="--",
                                     font=("Arial", 12))
        self.change_label.pack()

    def start(self):
        """Start WebSocket connection."""
        if self.is_active:
            return

        self.is_active = True
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"{self.symbol} error: {err}"),
            on_close=lambda ws, s, m: print(f"{self.symbol} closed"),
            on_open=lambda ws: print(f"{self.symbol} connected")
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        """Stop WebSocket connection."""
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        """Handle price updates."""
        if not self.is_active:
            return

        data = json.loads(message)
        price = float(data['c'])
        change = float(data['p'])
        percent = float(data['P'])

        # Schedule GUI update on main thread
        self.parent.after(0, self.update_display, price, change, percent)

    def update_display(self, price, change, percent):
        """Update the ticker display."""
        if not self.is_active:
            return

        color = "green" if change >= 0 else "red"
        self.price_label.config(text=f"{price:,.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color
        )

    def pack(self, **kwargs):
        """Allow easy placement of ticker."""
        self.frame.pack(**kwargs)

    def pack_forget(self):
        """Hide the ticker."""
        self.frame.pack_forget()


class CryptoDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("800x300")

        # Track tickers
        self.tickers = {}

        # 6 cryptos
        self.cryptos = {
            "btcusdt": "Bitcoin (BTC)",
            "ethusdt": "Ethereum (ETH)",
            "solusdt": "Solana (SOL)",
            "usdtusd": "Tether (USDT)",
            "usdcusdt": "USD Coin (USDC)",
            "bnbusdt": "Binance (BNB)"
        }

        # Setup UI
        self.setup_ui()

        # Start with BTC
        self.show_ticker("btcusdt")

    def setup_ui(self):
        # Control panel
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        # Create 6 buttons
        for symbol, name in self.cryptos.items():
            btn = ttk.Button(
                control_frame,
                text=name,
                command=lambda s=symbol: self.show_ticker(s)
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Ticker panel
        self.ticker_frame = ttk.Frame(self.root, padding=20)
        self.ticker_frame.pack(fill=tk.BOTH, expand=True)

    def show_ticker(self, symbol):
        """Show only one ticker at a time."""
        # Remove current ticker
        for ticker in self.tickers.values():
            ticker.stop()
            ticker.pack_forget()

        # Clear current tickers
        self.tickers.clear()

        # Add new ticker
        ticker = CryptoTicker(
            self.ticker_frame,
            symbol,
            self.cryptos[symbol]
        )
        ticker.pack(fill=tk.BOTH, expand=True)
        ticker.start()

        self.tickers[symbol] = ticker

    def on_closing(self):
        """Clean up when closing."""
        for ticker in self.tickers.values():
            ticker.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
