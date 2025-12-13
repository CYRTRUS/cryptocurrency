import tkinter as tk
import json
import threading
import websocket
from .debug import log

DARK_BG = "#242a24"
WHITE = "#ffffff"
GREEN = "#57b045"
RED = "#ff4444"
FONT = ("Courier New", 11, "bold")


class LastTradePanel:
    def __init__(self, parent, symbol):
        self.parent = parent
        self.symbol = symbol.lower()
        self.running = True

        self.frame = tk.Frame(parent, bg=DARK_BG, padx=10, pady=10)

        self.label = tk.Label(
            self.frame,
            font=FONT,
            bg=DARK_BG,
            fg=WHITE,
            anchor="w"
        )
        self.label.pack(fill=tk.X)

        log("TRADE", f"Starting WebSocket for {self.symbol.upper()}")

        self.ws = websocket.WebSocketApp(
            f"wss://stream.binance.com:9443/ws/{self.symbol}@trade",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close_ws
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_message(self, ws, message):
        if not self.running:
            return
        try:
            data = json.loads(message)
            price = float(data["p"])
            qty = float(data["q"])
            trade_type = "SELL" if data["m"] else "BUY"
            color = RED if trade_type == "SELL" else GREEN
            text = f"Last trade : {trade_type:<5} {qty:>7,.4f} at ${price:,.3f}"
            self.parent.after(0, lambda t=text, c=color: self.safe_update(t, c))
        except Exception as e:
            log("TRADE", f"Parse error {e}")

    def safe_update(self, text, color):
        if self.running and getattr(self, "label", None) and self.label.winfo_exists():
            self.label.config(text=text, fg=color)

    def on_error(self, ws, error):
        log("TRADE", f"WebSocket error {error}")

    def on_close_ws(self, ws, *args):
        log("TRADE", "WebSocket closed")

    def stop(self):
        log("LAST TRADE", "Stopping")
        self.running = False
        try:
            self.ws.close()
        except:
            pass
