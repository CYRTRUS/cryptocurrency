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
from lib.chart import CryptoChart  # <-- Chart import

# ================= COLORS =================
DARK_BG = "#1d221d"
LIGHT_BG = "#242a24"
GREEN = "#199400"
DARK_GREEN = "#104006"
HOVER_GREEN = "#155a15"
WHITE = "#ffffff"
GRAY = "#9c9c9c"
RED = "#ff4444"
LIGHT_RED = "#ff6666"

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
        self.chart_panel = None  # Chart reference
        self.current_symbol = self.load_setting()
        self.initialized = False  # <-- Track first load

        self.setup_ui()
        self.switch_symbol(self.current_symbol)  # First load
        self.initialized = True  # Now further reloads will check for same symbol

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

            # Hover handlers
            btn.bind("<Enter>", lambda e, s=sym, b=btn: self.on_hover_enter(s, b))
            btn.bind("<Leave>", lambda e, s=sym, b=btn: self.on_hover_leave(s, b))

            self.buttons[sym] = btn

        main = tk.Frame(self.root, bg=DARK_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left = tk.Frame(main, bg=DARK_BG, width=600)
        self.left.pack(side=tk.LEFT, fill=tk.Y)
        self.left.pack_propagate(False)

        self.right = tk.Frame(main, bg=LIGHT_BG)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Label(
            self.right,
            text="----- 1 Hour Candlestick Chart -----",
            font=("Courier New", 16, "bold"),
            bg=LIGHT_BG,
            fg=WHITE
        ).pack(expand=True, pady=10)

    # ================= HOVER =================
    def on_hover_enter(self, symbol, button):
        if symbol != self.current_symbol:
            button.config(bg=HOVER_GREEN)

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

        # Clear chart
        if self.chart_panel:
            self.chart_panel.stop()
            self.chart_panel.frame.destroy()
            self.chart_panel = None

    def switch_symbol(self, symbol):
        # ---------- SAME SYMBOL CHECK ----------
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
            OrderBookPanel(self.left, symbol),
            LastTradePanel(self.left, symbol)
        ]

        for p in panels:
            p.frame.pack(fill=tk.X, pady=5)
            self.active_panels.append(p)

        # Chart panel
        self.chart_panel = CryptoChart(self.right, symbol)

        # Update buttons
        for s, btn in self.buttons.items():
            if s == symbol:
                btn.config(bg=GREEN, fg=WHITE)
            else:
                btn.config(bg=DARK_GREEN, fg=GRAY)

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
