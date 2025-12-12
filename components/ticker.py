import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading


class CryptoTicker:
    """Reusable ticker component for any cryptocurrency."""

    def __init__(self, parent, symbol, display_name, initial_data=None):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.ws = None
        self.is_connected = False
        self.should_be_visible = True  # Track if UI should be shown

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
        self.change_label = ttk.Label(self.frame, text="--",
                                      font=("Arial", 12))
        self.change_label.pack()

        # Set initial data if provided
        if initial_data:
            self.update_display(
                initial_data['price'],
                initial_data['change'],
                initial_data['percent']
            )

    def connect(self):
        """Start WebSocket connection (call once at startup)."""
        if self.ws:
            return

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def disconnect(self):
        """Stop WebSocket connection."""
        if self.ws and self.is_connected:
            try:
                self.is_connected = False
                self.ws.close()
                print(f"{self.symbol} disconnected")
            except Exception as e:
                print(f"Error disconnecting {self.symbol}: {e}")
            finally:
                self.ws = None

    def on_open(self, ws):
        """Called when WebSocket connects."""
        self.is_connected = True
        print(f"{self.symbol} connected")

    def on_message(self, ws, message):
        """Handle price updates."""
        if not self.ws or not self.is_connected:
            return

        data = json.loads(message)
        price = float(data['c'])
        change = float(data['p'])
        percent = float(data['P'])

        # Only update GUI if ticker should be visible
        if self.should_be_visible:
            self.parent.after(0, self.update_display, price, change, percent)

    def on_error(self, ws, error):
        print(f"{self.symbol} error: {error}")

    def on_close(self, ws, status, msg):
        self.is_connected = False

    def update_display(self, price, change, percent):
        """Update the ticker display."""
        if not hasattr(self, 'price_label'):  # Safety check
            return

        color = "green" if change >= 0 else "red"
        self.price_label.config(text=f"{price:,.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color
        )

    def show(self):
        """Show the ticker UI."""
        self.should_be_visible = True
        self.frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

    def hide(self):
        """Hide the ticker UI."""
        self.should_be_visible = False
        self.frame.pack_forget()

    # Keep for compatibility
    def pack(self, **kwargs):
        """Allow easy placement of ticker."""
        self.frame.pack(**kwargs)

    def pack_forget(self):
        """Hide the ticker."""
        self.frame.pack_forget()
