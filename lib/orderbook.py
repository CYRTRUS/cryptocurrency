import tkinter as tk
import json
import threading
import websocket
from .debug import log

DARK_BG = "#242a24"
GREEN = "#57b045"
LIGHT_GREEN = "#76a96c"
RED = "#ff4444"
LIGHT_RED = "#ffa8a8"
WHITE = "#ffffff"
FONT_BIG = ("Courier New", 16, "bold")
FONT_SMALL = ("Courier New", 10, "bold")


class OrderBookPanel:
    def __init__(self, parent, symbol):
        self.parent = parent
        self.symbol = symbol.lower()
        self.running = True

        self.frame = tk.Frame(parent, bg=DARK_BG, padx=10, pady=10)
        container = tk.Frame(self.frame, bg=DARK_BG)
        container.pack(fill=tk.X)

        self.bids = tk.Frame(container, bg=DARK_BG)
        self.asks = tk.Frame(container, bg=DARK_BG)

        self.bids.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.asks.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        self.ws = websocket.WebSocketApp(
            f"wss://stream.binance.com:9443/ws/{self.symbol}@depth10@1000ms",
            on_message=self.on_message
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def on_message(self, ws, message):
        if not self.running:
            return
        try:
            data = json.loads(message)
            self.parent.after(0, lambda d=data: self.update_ui(d))
        except Exception as e:
            log("ORDERBOOK", f"Error {e}")

    @staticmethod
    def format_qty(qty: float) -> str:
        """Format quantity using K, M for large numbers."""
        if qty >= 1_000_000:
            return f"{qty / 1_000_000:.1f}M"
        elif qty >= 1_000:
            return f"{qty / 1_000:.1f}K"
        else:
            return f"{qty:,.3f}"

    def update_ui(self, data):
        if not self.running:
            return

        # Clear old widgets
        for f in (self.bids, self.asks):
            for w in f.winfo_children():
                w.destroy()

        # Bids
        tk.Label(self.bids, text="Top 10 Bids", fg=GREEN, bg=DARK_BG, font=FONT_BIG).pack(anchor="w")
        for p, q in data["bids"]:
            qty_str = self.format_qty(float(q))
            tk.Label(
                self.bids,
                text=f"${float(p):>11,.3f}{"Qty":>6} {qty_str:>8}",
                fg=LIGHT_GREEN, bg=DARK_BG, font=FONT_SMALL
            ).pack(anchor="w")

        # Asks
        tk.Label(self.asks, text="Top 10 Asks", fg=RED, bg=DARK_BG, font=FONT_BIG).pack(anchor="w")
        for p, q in data["asks"]:
            qty_str = self.format_qty(float(q))
            tk.Label(
                self.asks,
                text=f"${float(p):>11,.3f}{"Qty":>6} {qty_str:>8}",
                fg=LIGHT_RED, bg=DARK_BG, font=FONT_SMALL
            ).pack(anchor="w")

    def stop(self):
        log("ORDERBOOK", "Stopping")
        self.running = False
        try:
            self.ws.close()
        except:
            pass
