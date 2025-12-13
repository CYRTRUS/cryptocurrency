import tkinter as tk
import json
import os

from lib import (
    CryptoTicker,
    VolumePanel,
    OrderBookPanel,
    LastTradePanel,
    log
)
from lib.chart import CryptoChart

# ================= COLORS =================
LIGHT_BG = "#242a24"
DARK_BG = "#1d221d"
LIGHT_GREEN = "#73BD64"  # hover color for crypto buttons
GREEN = "#199400"
DARK_GREEN = "#104006"
WHITE = "#ffffff"
GRAY = "#9c9c9c"
RED = "#ff4444"
LIGHT_RED = "#ff6666"
YELLOW = "#ffc800"
LIGHT_YELLOW = "#ffe587"
DARK_YELLOW = "#8d6e00"

FONT = ("Courier New", 11, "bold")
TITLE_FONT = ("Courier New", 18, "bold")

SETTINGS_FILE = "setting.json"


class CryptoDashboard:
    def __init__(self, root):
        log("MAIN", "App started")

        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("1400x700")
        self.root.minsize(1400, 700)
        self.root.configure(bg=DARK_BG)

        self.symbols = {
            "btcusdt": "Bitcoin (BTC)",
            "ethusdt": "Ethereum (ETH)",
            "solusdt": "Solana (SOL)",
            "bnbusdt": "Binance Coin (BNB)",
            "xrpusdt": "Ripple (XRP)",
            "usdcusdt": "USD Coin (USDC)"
        }

        self.buttons = {}
        self.active_panels = []
        self.chart_panel = None
        self.current_symbol = self.load_setting()
        self.initialized = False

        self.chart_visible = True
        self.orderbook_visible = True

        self.setup_ui()
        self.switch_symbol(self.current_symbol)
        self.initialized = True

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ================= UI =================
    def setup_ui(self):
        header = tk.Frame(self.root, bg=DARK_BG)
        header.pack(fill=tk.X)

        self.title = tk.Label(
            header,
            font=TITLE_FONT,
            fg=WHITE,
            bg=DARK_BG,
            padx=20
        )
        self.title.pack(side=tk.LEFT)

        close_btn = tk.Button(
            header,
            text="X",
            font=("Courier New", 12, "bold"),
            bg=RED,
            fg=WHITE,
            bd=0,
            command=self.on_close
        )
        close_btn.pack(side=tk.RIGHT, padx=15)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=LIGHT_RED))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=RED))

        # Crypto buttons
        btn_frame = tk.Frame(self.root, bg=DARK_BG)
        btn_frame.pack(fill=tk.X, pady=5)

        for sym, name in self.symbols.items():
            btn = tk.Button(
                btn_frame,
                text=name,
                font=FONT,
                bg=DARK_GREEN,
                fg=GRAY,
                relief="flat",
                command=lambda s=sym: self.switch_symbol(s)
            )
            btn.pack(side=tk.LEFT, padx=8)
            btn.bind("<Enter>", lambda e, s=sym, b=btn: self.on_hover_enter(s, b))
            btn.bind("<Leave>", lambda e, s=sym, b=btn: self.on_hover_leave(s, b))
            self.buttons[sym] = btn

        # Toggle buttons: OrderBook first, Chart second
        self.orderbook_toggle_btn = tk.Button(
            btn_frame,
            text="OrderBook",
            font=FONT,
            fg="black",
            bg=YELLOW,
            width=10,
            height=1,
            relief="flat",
            command=self.toggle_orderbook
        )
        self.orderbook_toggle_btn.pack(side=tk.LEFT, padx=5)
        self.orderbook_toggle_btn.bind("<Enter>", lambda e: self.orderbook_toggle_btn.config(bg=LIGHT_YELLOW))
        self.orderbook_toggle_btn.bind("<Leave>", lambda e: self.orderbook_toggle_btn.config(
            bg=YELLOW if self.orderbook_visible else DARK_YELLOW))

        self.chart_toggle_btn = tk.Button(
            btn_frame,
            text="Chart",
            font=FONT,
            fg="black",
            bg=YELLOW,
            width=10,
            height=1,
            relief="flat",
            command=self.toggle_chart
        )
        self.chart_toggle_btn.pack(side=tk.LEFT, padx=5)
        self.chart_toggle_btn.bind("<Enter>", lambda e: self.chart_toggle_btn.config(bg=LIGHT_YELLOW))
        self.chart_toggle_btn.bind("<Leave>", lambda e: self.chart_toggle_btn.config(
            bg=YELLOW if self.chart_visible else DARK_YELLOW))

        main = tk.Frame(self.root, bg=DARK_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left = tk.Frame(main, bg=DARK_BG, width=600)
        self.left.pack(side=tk.LEFT, fill=tk.Y)
        self.left.pack_propagate(False)

        self.right = tk.Frame(main, bg=LIGHT_BG)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Right header (small, not expanding)
        self.right_header = tk.Frame(self.right, bg=LIGHT_BG)
        self.right_header.pack(fill=tk.X)
        tk.Label(
            self.right_header,
            text="——— 1 Hour Candlestick Chart ———",
            font=("Courier New", 16, "bold"),
            bg=LIGHT_BG,
            fg=WHITE
        ).pack(expand=True, pady=10)

        self.right_chart_container = tk.Frame(self.right, bg=LIGHT_BG)
        self.right_chart_container.pack(fill=tk.BOTH, expand=True)

    # ================= HOVER =================
    def on_hover_enter(self, symbol, button):
        if symbol != self.current_symbol:
            button.config(fg=WHITE, bg=LIGHT_GREEN)

    def on_hover_leave(self, symbol, button):
        if symbol == self.current_symbol:
            button.config(bg=GREEN, fg=WHITE)
        else:
            button.config(bg=DARK_GREEN, fg=GRAY)

    # ================= PANELS =================
    def clear_panels(self):
        for p in self.active_panels:
            p.stop()
            p.frame.destroy()
        self.active_panels.clear()

        if self.chart_panel:
            self.chart_panel.stop()
            self.chart_panel.frame.destroy()
            self.chart_panel = None

    def switch_symbol(self, symbol):
        if self.initialized and symbol == self.current_symbol:
            log("MAIN", f"Symbol {symbol.upper()} already active, skipping reload")
            return

        log("MAIN", f"Switching symbol -> {symbol.upper()}")
        self.current_symbol = symbol
        self.title.config(text=f"{self.symbols[symbol]} Dashboard")

        self.clear_panels()

        panels = [
            CryptoTicker(self.left, symbol, self.symbols[symbol]),
            VolumePanel(self.left, symbol),
            LastTradePanel(self.left, symbol),
            OrderBookPanel(self.left, symbol)
        ]

        for p in panels:
            p.frame.pack(fill=tk.X, pady=5)
            self.active_panels.append(p)

        self.chart_panel = CryptoChart(self.right_chart_container, symbol)

        for s, btn in self.buttons.items():
            if s == symbol:
                btn.config(bg=GREEN, fg=WHITE)
            else:
                btn.config(bg=DARK_GREEN, fg=GRAY)

    # ================= TOGGLE BUTTONS =================
    def toggle_chart(self):
        if self.chart_panel:
            if self.chart_visible:
                self.chart_panel.frame.pack_forget()
                log("TOGGLE", f"Chart hidden for {self.current_symbol.upper()}")
            else:
                self.chart_panel.frame.pack(fill=tk.BOTH, expand=True)
                log("TOGGLE", f"Chart shown for {self.current_symbol.upper()}")
            self.chart_visible = not self.chart_visible
            self.chart_toggle_btn.config(bg=YELLOW if self.chart_visible else DARK_YELLOW)

    def toggle_orderbook(self):
        for p in self.active_panels:
            if p.__class__.__name__ == "OrderBookPanel":
                p.set_visible(not self.orderbook_visible)
                log("TOGGLE", f"OrderBook {'shown' if not self.orderbook_visible else 'hidden'} for {self.current_symbol.upper()}")
        self.orderbook_visible = not self.orderbook_visible
        self.orderbook_toggle_btn.config(bg=YELLOW if self.orderbook_visible else DARK_YELLOW)

    # ================= SETTINGS =================
    def load_setting(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE) as f:
                    return json.load(f).get("last_symbol", "btcusdt")
            except:
                pass
        return "btcusdt"

    def on_close(self):
        log("MAIN", "Closing application")
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"last_symbol": self.current_symbol}, f, indent=2)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    CryptoDashboard(root)
    root.mainloop()
