import tkinter as tk
import json
import threading
import websocket

from .debug import log

DARK_BG = "#242a24"
WHITE = "#ffffff"
GREEN = "#57b045"
RED = "#ff4444"
FONT = ("Courier New", 13, "bold")


class CryptoTicker:
    def __init__(self, parent, symbol, name):
        self.parent = parent
        self.symbol = symbol.lower()
        self.running = True

        log("TICKER", f"Connecting WebSocket {self.symbol}@ticker")

        self.frame = tk.Frame(parent, bg=DARK_BG, padx=10, pady=10)

        tk.Label(
            self.frame,
            text=name,
            font=FONT,
            bg=DARK_BG,
            fg=WHITE
        ).pack(anchor="w")

        self.price_label = tk.Label(
            self.frame,
            font=("Courier New", 16, "bold"),
            bg=DARK_BG,
            fg=WHITE
        )
        self.price_label.pack(anchor="w", pady=4)

        self.change_label = tk.Label(
            self.frame,
            font=("Courier New", 11, "bold"),
            bg=DARK_BG,
            fg=WHITE
        )
        self.change_label.pack(anchor="w")

        self.ws = websocket.WebSocketApp(
            f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker",
            on_message=self.on_message
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_message(self, ws, message):
        if not self.running:
            return

        data = json.loads(message)
        price = float(data["c"])
        change = float(data["P"])
        color = GREEN if change >= 0 else RED
        sign = "+" if change >= 0 else ""

        self.parent.after(0, lambda: self.safe_update(price, change, sign, color))

    def safe_update(self, price, change, sign, color):
        if self.running and getattr(self, "price_label", None) and self.price_label.winfo_exists():
            self.price_label.config(text=f"Current price ${price:,.2f}", fg=color)
            self.change_label.config(text=f"24h Change : {sign}{change:.2f}%", fg=color)

    def stop(self):
        log("TICKER", "Closing WebSocket")
        self.running = False
        try:
            self.ws.close()
        except:
            pass
