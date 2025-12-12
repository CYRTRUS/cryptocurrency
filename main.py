import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
import time
import os


class CryptoTicker:
    """Reusable ticker component for any cryptocurrency."""

    def __init__(self, parent, symbol, display_name):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.is_active = False
        self.ws = None
        self.last_data = None  # Store last received data
        self.connection_established = False  # Track if connection is established

        # Rate limiting variables
        self.last_update_time = 0
        self.update_interval = 0.2  # 5 times per second (1/5 = 0.2 seconds)
        self.pending_update = None  # Store pending update data

        # Create UI
        frame_bg = "#242A24"
        self.frame = tk.Frame(parent, relief="solid", borderwidth=2,
                              bg=frame_bg,
                              padx=20, pady=20)

        # Title
        tk.Label(self.frame, text=display_name,
                 font=("Arial", 16, "bold"),
                 bg=frame_bg,
                 fg="white"
                 ).pack()

        # Price
        self.price_label = tk.Label(self.frame, text="--,---",
                                    font=("Arial", 40, "bold"),
                                    bg=frame_bg,
                                    fg="white"
                                    )
        self.price_label.pack(pady=10)

        # Change
        self.change_label = tk.Label(self.frame, text="--",
                                     font=("Arial", 12),
                                     bg=frame_bg,
                                     fg="white")
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
            on_close=lambda ws, s, m: self.on_close(),
            on_open=lambda ws: self.on_open()
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_open(self):
        """Handle WebSocket connection open."""
        print(f"{self.symbol} connected")
        self.connection_established = True

    def on_close(self):
        """Handle WebSocket connection close."""
        print(f"{self.symbol} closed")
        self.connection_established = False

    def stop(self):
        """Stop WebSocket connection."""
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        """Handle price updates with rate limiting."""
        if not self.is_active:
            return

        data = json.loads(message)
        self.last_data = data  # Store the data

        # Get current time
        current_time = time.time()

        # Check if enough time has passed since last update
        if current_time - self.last_update_time >= self.update_interval:
            # Enough time has passed, process immediately
            self.last_update_time = current_time
            price = float(data['c'])
            change = float(data['p'])
            percent = float(data['P'])

            # Schedule GUI update on main thread
            self.parent.after(0, self.update_display, price, change, percent)
            self.pending_update = None  # Clear any pending update
        else:
            # Rate limit exceeded, store the latest data for later
            self.pending_update = data

            # Calculate when we should process the next update
            time_to_wait = self.update_interval - \
                (current_time - self.last_update_time)

            # Schedule a delayed update
            self.parent.after(int(time_to_wait * 1000),
                              self.process_pending_update)

    def process_pending_update(self):
        """Process a pending update that was rate-limited."""
        if self.pending_update and self.is_active:
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                self.last_update_time = current_time
                price = float(self.pending_update['c'])
                change = float(self.pending_update['p'])
                percent = float(self.pending_update['P'])

                self.parent.after(0, self.update_display,
                                  price, change, percent)
                self.pending_update = None  # Clear after processing

    def update_display(self, price, change, percent):
        """Update the ticker display."""
        if not self.is_active:
            return

        color = "#15FA00" if change >= 0 else "#FF1100"  # Green/Red colors
        self.price_label.config(text=f"${price:,.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color
        )

    def show_last_data(self):
        """Display the last received data if available."""
        if self.last_data:
            price = float(self.last_data['c'])
            change = float(self.last_data['p'])
            percent = float(self.last_data['P'])
            self.update_display(price, change, percent)

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
        self.root.geometry("1200x600")
        self.root.configure(bg="#D0FF00")  # Set main window background

        # Track tickers and buttons
        self.tickers = {}
        self.buttons = {}
        self.current_symbol = None  # Track currently displayed crypto
        self.data_file = "crypto_prices.json"  # File to save/load prices

        # 6 cryptos
        self.cryptos = {
            "btcusdt": "Bitcoin (BTC)",
            "ethusdt": "Ethereum (ETH)",
            "solusdt": "Solana (SOL)",
            "usdtusd": "Tether (USDT)",
            "usdcusdt": "USD Coin (USDC)",
            "bnbusdt": "Binance (BNB)"
        }

        # Load saved prices from file
        self.saved_prices = self.load_prices()

        # Setup UI
        self.setup_ui()

        # Start ALL tickers immediately
        for symbol in self.cryptos.keys():
            self.create_ticker(symbol)

        # Show Bitcoin ticker on startup with saved data if available
        self.show_ticker("btcusdt")

    def load_prices(self):
        """Load saved prices from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"Error loading {self.data_file}, starting fresh")
                return {}
        return {}

    def save_prices(self):
        """Save current prices to JSON file."""
        try:
            prices_to_save = {}
            for symbol, ticker in self.tickers.items():
                if ticker.last_data:
                    prices_to_save[symbol] = {
                        'price': ticker.last_data['c'],
                        'change': ticker.last_data['p'],
                        'percent': ticker.last_data['P'],
                        'timestamp': time.time()
                    }

            with open(self.data_file, 'w') as f:
                json.dump(prices_to_save, f, indent=2)

            print(f"Prices saved to {self.data_file}")
        except Exception as e:
            print(f"Error saving prices: {e}")

    def setup_ui(self):
        # Control panel - using tk.Frame for color
        control_frame = tk.Frame(self.root, bg="#1D221D", pady=10, padx=10)
        control_frame.pack(fill=tk.X)

        # Create 6 buttons with tk.Button
        for symbol, name in self.cryptos.items():
            btn = tk.Button(
                control_frame,
                text=name,
                command=lambda s=symbol: self.show_ticker(s),
                bg="#15FA00",      # Background color - default bright green
                fg="white",        # Text color
                font=("Arial", 10, "bold"),
                padx=15,
                pady=5,
                relief="flat",
                activebackground="#87FF7C",  # Color when pressed
                activeforeground="black"
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons[symbol] = btn

        # Ticker panel - using tk.Frame
        self.ticker_frame = tk.Frame(self.root, bg="#1D221D")
        self.ticker_frame.pack(fill=tk.BOTH, expand=True)

    def create_ticker(self, symbol):
        """Create a ticker and start its WebSocket connection."""
        ticker = CryptoTicker(
            self.ticker_frame,
            symbol,
            self.cryptos[symbol]
        )

        # Load saved data if available
        if symbol in self.saved_prices:
            saved_data = self.saved_prices[symbol]
            # Create a mock last_data structure
            ticker.last_data = {
                'c': saved_data['price'],
                'p': saved_data['change'],
                'P': saved_data['percent']
            }
            print(f"Loaded saved price for {symbol}: {saved_data['price']}")

        # Initially hide the ticker
        ticker.frame.pack_forget()
        ticker.start()
        self.tickers[symbol] = ticker

    def update_button_colors(self, active_symbol):
        """Update button colors - active button is brighter, others are darker."""
        darker_green = "#0A7A00"  # Darker green for inactive buttons
        darker_text = "#CCCCCC"   # Darker text color for inactive buttons

        for symbol, button in self.buttons.items():
            if symbol == active_symbol:
                # Active button - brighter green and white text
                button.config(bg="#15FA00", fg="white",
                              activebackground="#87FF7C", activeforeground="white")
            else:
                # Inactive buttons - darker green and darker text
                button.config(bg=darker_green, fg=darker_text,
                              activebackground="#4CAF50", activeforeground="white")

    def show_ticker(self, symbol):
        """Show only one ticker at a time."""
        # Update button colors
        self.update_button_colors(symbol)
        self.current_symbol = symbol

        # Hide all tickers
        for ticker in self.tickers.values():
            ticker.frame.pack_forget()

        # Show the selected ticker
        selected_ticker = self.tickers[symbol]
        selected_ticker.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Show last received data if available
        selected_ticker.show_last_data()

    def on_closing(self):
        """Clean up when closing."""
        # Save current prices before closing
        self.save_prices()

        # Stop all tickers
        for ticker in self.tickers.values():
            ticker.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoDashboard(root)

    # Auto-save every 30 seconds
    def auto_save():
        app.save_prices()
        root.after(30000, auto_save)  # Schedule next save in 30 seconds

    root.after(30000, auto_save)  # Start auto-save

    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
