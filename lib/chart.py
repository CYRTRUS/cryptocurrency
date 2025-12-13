import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np
import requests
from datetime import datetime
import threading
from matplotlib.ticker import FuncFormatter, MaxNLocator
from .debug import log
from .base_panel import BasePanel

# ================= COLORS =================
DARK_BG = "#242a24"
WHITE = "#ffffff"
GREEN = "#57b045"
RED = "#ff4444"
GRAY = "#b5b5b5"

PRICE_FONT_SIZE = 12
LABEL_FONT_SIZE = 9
MIN_CANDLE_RATIO = 0.01
UPDATE_INTERVAL = 3  # seconds


class CryptoChart(BasePanel):
    def __init__(self, parent, symbol, interval="1m", limit=60):
        super().__init__(parent)
        self.symbol = symbol.upper()
        self.interval = interval
        self.limit = limit
        self.prev_price = None

        log("CHART", f"Initializing chart for {self.symbol}")

        self.frame.config(bg=DARK_BG)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Candlestick chart
        self.fig = Figure(figsize=(6, 3), dpi=100, facecolor=DARK_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(DARK_BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Volume chart
        self.fig2 = Figure(figsize=(6, 1.5), dpi=100, facecolor=DARK_BG)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_facecolor(DARK_BG)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.frame)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.ax.yaxis.set_major_formatter(FuncFormatter(self.price_formatter))
        self.ax2.yaxis.set_major_formatter(FuncFormatter(self.volume_formatter))

        # Start update loop
        threading.Thread(target=self.update_loop, daemon=True).start()

    # ---------------- Formatters ----------------
    @staticmethod
    def price_formatter(x, pos):
        if x >= 10:
            return f"{x:,.0f}"
        elif x >= 1:
            return f"{x:,.2f}"
        else:
            return f"{x:,.4f}"

    @staticmethod
    def volume_formatter(x, pos):
        if x >= 1_000_000:
            return f"{x/1_000_000:.0f}M"
        elif x >= 1_000:
            return f"{x/1_000:.0f}K"
        elif x > 0:
            return f"{x:.2f}"
        else:
            return "0"

    # ---------------- Fetch klines ----------------
    def fetch_klines(self):
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": self.symbol, "interval": self.interval, "limit": self.limit}
            return requests.get(url, params=params, timeout=5).json()
        except Exception as e:
            log("CHART", f"Error fetching klines: {e}")
            return []

    # ---------------- Plotting ----------------
    def plot(self, klines):
        if not klines:
            return

        ts = [datetime.fromtimestamp(k[0]/1000) for k in klines]
        data = np.array(klines)[:, 1:5].astype(float)
        vol_data = np.array(klines)[:, 5].astype(float)

        self.ax.clear()
        self.ax2.clear()

        for spine in self.ax.spines.values():
            spine.set_color(GRAY)
        for spine in self.ax2.spines.values():
            spine.set_color(GRAY)

        width = 0.6

        for i, (o, h, l, c) in enumerate(data):
            color = GREEN if c >= o else RED
            candle_height = max(abs(c - o), (h - l) * MIN_CANDLE_RATIO)
            y_bottom = min(o, c) if abs(c - o) >= (h - l) * MIN_CANDLE_RATIO else min(o, c) - (candle_height - abs(c - o))/2
            self.ax.plot([i, i], [l, h], color=color, linewidth=1)
            rect = patches.Rectangle((i - width/2, y_bottom), width, candle_height, facecolor=color)
            self.ax.add_patch(rect)

        price = data[-1, 3]
        min_p, max_p = data[:, 2].min(), data[:, 1].max()
        buffer = (max_p - min_p) * 0.2 if max_p != min_p else max_p * 0.02
        ymin = min(min_p - buffer, price - buffer*1.5)
        ymax = max(max_p + buffer, price + buffer*1.5)
        self.ax.set_ylim(ymin, ymax)
        self.ax.yaxis.set_major_locator(MaxNLocator(nbins=6, prune='both'))

        line_color = GREEN if self.prev_price is None or price >= self.prev_price else RED
        self.ax.axhline(price, color=line_color, linestyle="--", linewidth=1)
        self.ax.text(
            1.01, price, f"{price:,.4f}",
            transform=self.ax.get_yaxis_transform(),
            color=line_color,
            va="center", ha="left",
            fontdict={"family": "Courier New", "size": PRICE_FONT_SIZE, "weight": "bold"},
            bbox=dict(facecolor=DARK_BG)
        )

        self.ax.set_facecolor(DARK_BG)
        self.ax.set_ylabel("Price", fontdict={"family": "Courier New", "size": LABEL_FONT_SIZE,
                                              "weight": "bold", "color": GRAY})
        self.ax.grid(True, color="gray", linestyle="--", linewidth=0.3)
        self.ax.tick_params(axis='y', colors=GRAY)
        self.ax.get_xaxis().set_visible(False)

        self.ax2.bar(range(len(vol_data)), vol_data, color=[GREEN if c >= o else RED for o, h, l, c in data])
        tick_spacing = max(1, len(ts)//6)
        tick_labels = [t.strftime("%H:%M") for t in ts]
        self.ax2.set_xticks(np.arange(0, len(tick_labels), tick_spacing))
        self.ax2.set_xticklabels(tick_labels[::tick_spacing], rotation=30, ha="right",
                                 fontdict={"family": "Courier New", "size": LABEL_FONT_SIZE,
                                           "weight": "bold", "color": GRAY})
        self.ax2.set_facecolor(DARK_BG)
        self.ax2.set_ylabel("Volume", fontdict={"family": "Courier New", "size": LABEL_FONT_SIZE,
                                                "weight": "bold", "color": GRAY})
        self.ax2.tick_params(axis='y', colors=GRAY)
        self.ax2.tick_params(axis='x', colors=GRAY)
        self.ax2.grid(True, color="gray", linestyle="--", linewidth=0.3)

        try:
            self.fig.tight_layout(pad=0.3)
            self.fig2.tight_layout(pad=0.3)
        except:
            pass

        self.canvas.draw()
        self.canvas2.draw()
        self.prev_price = price

    # ---------------- Update Loop ----------------
    def update_loop(self):
        while self.running:
            klines = self.fetch_klines()
            if klines:
                self.safe_update(self.plot, klines)
            threading.Event().wait(UPDATE_INTERVAL)
