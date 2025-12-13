# lib/chart.py
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np
import requests
from datetime import datetime
import threading
import websocket
import json
from .debug import log

# ================= COLORS =================
DARK_BG = "#242a24"
WHITE = "#ffffff"
GREEN = "#57b045"
RED = "#ff4444"
GRAY = "#b5b5b5"

FONT = ("Courier New", 8, "bold")  # Axis label font
PRICE_FONT_SIZE = 12  # Current price font
MIN_CANDLE_RATIO = 0.01  # Minimum candle height ratio to interval


class CryptoChart:
    def __init__(self, parent, symbol, interval="1m", limit=60):
        self.parent = parent
        self.symbol = symbol.upper()
        self.interval = interval
        self.limit = limit
        self.running = True
        self.current_price = None
        self.prev_price = None
        self.price_line = None
        self.price_text = None
        self.debug_logged = False

        log("CHART", f"Initializing chart for {self.symbol}")

        # Tkinter frame
        self.frame = tk.Frame(parent, bg=DARK_BG)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Main candlestick chart
        self.fig = Figure(figsize=(6, 3), dpi=100, facecolor=DARK_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(DARK_BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Volume chart
        self.fig2 = Figure(figsize=(6, 1), dpi=100, facecolor=DARK_BG)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_facecolor(DARK_BG)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.frame)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Start threads
        threading.Thread(target=self.rest_loop, daemon=True).start()
        threading.Thread(target=self.ws_price_loop, daemon=True).start()

    # ---------------- Fetch REST Candles ----------------
    def fetch_klines(self):
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": self.symbol, "interval": self.interval, "limit": self.limit}
            data = requests.get(url, params=params, timeout=5).json()
            return data
        except Exception as e:
            log("CHART", f"Error fetching klines: {e}")
            return []

    # ---------------- Plot Candles ----------------
    def plot(self, klines):
        if not klines:
            return

        ts = [datetime.fromtimestamp(k[0]/1000) for k in klines]
        data = np.array(klines)[:, 1:5].astype(float)  # OHLC
        vol_data = np.array(klines)[:, 5].astype(float)

        self.ax.clear()
        self.ax2.clear()

        for spine in self.ax.spines.values():
            spine.set_color(GRAY)
        for spine in self.ax2.spines.values():
            spine.set_color(GRAY)

        width = 0.6

        # Calculate dynamic y-axis
        all_prices = np.concatenate([data[:, 1:5].flatten(), [data[-1, 3]]])
        min_p = all_prices.min()
        max_p = all_prices.max()
        if max_p == min_p:
            max_p = min_p * 1.001  # Avoid zero interval
        interval = (max_p - min_p) / 10
        if interval < 0.0001:
            interval = 0.0001
        y_min = min_p - 2*interval
        y_max = max_p + 2*interval
        self.ax.set_ylim(y_min, y_max)

        # Determine decimal places for y-axis
        temp_in = interval
        n = 0
        while temp_in < 1:
            temp_in *= 10
            n += 1

        if not self.debug_logged:
            self.current_price = data[-1, 3]
            log("CHART", f"Min = {min_p:,.{n}f}, Max = {max_p:,.{n}f}, Curr = {self.current_price:,.2f}")
            self.debug_logged = True

        # Draw candlesticks with minimum height
        for i, (o, h, l, c) in enumerate(data):
            color = GREEN if c >= o else RED
            candle_height = abs(c - o)
            min_candle_height = max(interval * MIN_CANDLE_RATIO, 0.0001)
            if candle_height < min_candle_height:
                candle_height = min_candle_height
                y_bottom = min(o, c) - (min_candle_height - abs(c - o))/2
            else:
                y_bottom = min(o, c)
            self.ax.plot([i, i], [l, h], color=color, linewidth=1)
            rect = patches.Rectangle((i - width/2, y_bottom), width, candle_height, facecolor=color)
            self.ax.add_patch(rect)

        # Current price line color depends on change
        price = data[-1, 3]
        self.current_price = price
        if self.prev_price is None:
            line_color = GREEN
        else:
            line_color = GREEN if price >= self.prev_price else RED
        self.prev_price = price

        if self.price_line is None:
            self.price_line = self.ax.axhline(price, color=line_color, linestyle="--", linewidth=1)
            self.price_text = self.ax.text(
                1.01, price, f"{price:,.2f}",
                transform=self.ax.get_yaxis_transform(),
                color=line_color,
                va="center", ha="left",
                fontdict={"family": "Courier New", "size": PRICE_FONT_SIZE, "weight": "bold"},
                bbox=dict(facecolor=DARK_BG)
            )
        else:
            self.price_line.set_ydata([price]*2)
            self.price_line.set_color(line_color)
            self.price_text.set_y(price)
            self.price_text.set_text(f"{price:,.2f}")
            self.price_text.set_color(line_color)

        # Axis labels and grid
        self.ax.set_facecolor(DARK_BG)
        self.ax.set_ylabel("Price", fontdict={"family": "Courier New", "size": FONT[1], "weight": "bold", "color": GRAY})
        self.ax.grid(True, color="gray", linestyle="--", linewidth=0.3)
        self.ax.tick_params(axis='y', colors=GRAY)
        self.ax.get_xaxis().set_visible(False)
        self.ax.yaxis.set_major_formatter(lambda x, pos: f"{x:,.{n}f}")
        self.ax.autoscale_view()

        # Volume bars
        self.ax2.bar(range(len(vol_data)), vol_data, color=[GREEN if c >= o else RED for o, h, l, c in data])
        tick_spacing = max(1, len(ts)//6)
        tick_labels = [t.strftime("%H:%M") for t in ts]
        self.ax2.set_xticks(np.arange(0, len(tick_labels), tick_spacing))
        self.ax2.set_xticklabels(tick_labels[::tick_spacing], rotation=30, ha="right",
                                 fontdict={"family": "Courier New", "size": FONT[1], "weight": "bold", "color": GRAY})
        self.ax2.set_facecolor(DARK_BG)
        self.ax2.set_ylabel("Volume", fontdict={"family": "Courier New", "size": FONT[1], "weight": "bold", "color": GRAY})
        self.ax2.tick_params(axis='y', colors=GRAY)
        self.ax2.tick_params(axis='x', colors=GRAY)
        self.ax2.grid(True, color="gray", linestyle="--", linewidth=0.3)
        self.ax2.yaxis.set_major_formatter(lambda x, pos: f"{x:,.0f}")
        self.ax2.autoscale_view()

        self.fig.tight_layout()
        self.fig2.tight_layout()
        self.canvas.draw()
        self.canvas2.draw()

    # ---------------- REST Update Loop ----------------
    def rest_loop(self):
        while self.running:
            klines = self.fetch_klines()
            self.parent.after(0, lambda k=klines: self.plot(k))
            threading.Event().wait(60)

    # ---------------- WebSocket Price Update ----------------
    def ws_price_loop(self):
        def on_message(ws, message):
            if not self.running:
                return
            try:
                data = json.loads(message)
                price = float(data["c"])
                self.current_price = price
                if self.price_line:
                    line_color = GREEN if price >= self.prev_price else RED
                    self.price_line.set_ydata([price]*2)
                    self.price_line.set_color(line_color)
                    self.price_text.set_y(price)
                    self.price_text.set_text(f"{price:,.2f}")
                    self.price_text.set_color(line_color)
                    self.canvas.draw()
                self.prev_price = price
            except Exception as e:
                log("CHART", f"WebSocket parse error: {e}")

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@ticker"
        log("CHART", f"Connecting WebSocket for {self.symbol}")
        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        ws.run_forever()

    # ---------------- Calculate decimal places ----------------
    def get_decimal_places(self):
        y_min, y_max = self.ax.get_ylim()
        interval = (y_max - y_min) / 10
        temp_in = interval
        n = 0
        while temp_in < 1:
            temp_in *= 10
            n += 1
        return n

    def stop(self):
        log("CHART", f"Stopping chart for {self.symbol}")
        self.running = False
