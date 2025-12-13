import tkinter as tk
import json
import threading
import websocket
from .debug import log

# ================= COLORS =================
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
        self.data_visible = True  # only the data, not header

        self.frame = tk.Frame(parent, bg=DARK_BG, padx=10, pady=10)

        # Headers and data frames
        self.bids_frame = tk.Frame(self.frame, bg=DARK_BG)
        self.asks_frame = tk.Frame(self.frame, bg=DARK_BG)

        self.bids_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.asks_frame.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Header labels (always visible)
        self.bids_header = tk.Label(self.bids_frame, text="Top 10 Bids", fg=GREEN, bg=DARK_BG, font=FONT_BIG)
        self.bids_header.pack(anchor="w")
        self.asks_header = tk.Label(self.asks_frame, text="Top 10 Asks", fg=RED, bg=DARK_BG, font=FONT_BIG)
        self.asks_header.pack(anchor="w")

        # Data container frames (for packing/unpacking rows)
        self.bids_data = tk.Frame(self.bids_frame, bg=DARK_BG)
        self.asks_data = tk.Frame(self.asks_frame, bg=DARK_BG)
        self.bids_data.pack()
        self.asks_data.pack()

        # Start WebSocket
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
        if qty >= 1_000_000:
            return f"{qty / 1_000_000:.1f}M"
        elif qty >= 1_000:
            return f"{qty / 1_000:.1f}K"
        else:
            return f"{qty:,.3f}"

    def update_ui(self, data):
        if not self.running or not self.data_visible:
            return

        # Clear old rows
        for w in self.bids_data.winfo_children():
            w.destroy()
        for w in self.asks_data.winfo_children():
            w.destroy()

        # Bids rows
        for p, q in data["bids"]:
            qty_str = self.format_qty(float(q))
            tk.Label(
                self.bids_data,
                text=f"${float(p):>11,.3f}  Qty {qty_str:>8}",
                fg=LIGHT_GREEN, bg=DARK_BG, font=FONT_SMALL
            ).pack(anchor="w")

        # Asks rows
        for p, q in data["asks"]:
            qty_str = self.format_qty(float(q))
            tk.Label(
                self.asks_data,
                text=f"${float(p):>11,.3f}  Qty {qty_str:>8}",
                fg=LIGHT_RED, bg=DARK_BG, font=FONT_SMALL
            ).pack(anchor="w")

    def set_visible(self, visible: bool):
        """Toggle visibility of orderbook data (headers always visible)."""
        self.data_visible = visible
        if visible:
            self.bids_data.pack()
            self.asks_data.pack()
        else:
            self.bids_data.pack_forget()
            self.asks_data.pack_forget()

    def stop(self):
        log("ORDERBOOK", "Stopping")
        self.running = False
        try:
            self.ws.close()
        except:
            pass
