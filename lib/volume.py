import tkinter as tk
import threading
import requests
from .debug import log

DARK_BG = "#242a24"
WHITE = "#ffffff"
FONT = ("Courier New", 11, "bold")


def get_base_asset(symbol: str) -> str:
    symbol = symbol.upper()
    for quote in ("USDT", "USDC", "USD", "BUSD"):
        if symbol.endswith(quote):
            return symbol[:-len(quote)]
    return symbol


class VolumePanel:
    def __init__(self, parent, symbol):
        self.parent = parent
        self.symbol = symbol.upper()
        self.unit = get_base_asset(self.symbol)

        self.frame = tk.Frame(parent, bg=DARK_BG, padx=10, pady=10)

        self.label = tk.Label(
            self.frame,
            font=FONT,
            bg=DARK_BG,
            fg=WHITE,
            anchor="w"
        )
        self.label.pack(fill=tk.X)

        threading.Thread(target=self.fetch, daemon=True).start()

    def fetch(self):
        try:
            log("VOLUME", f"Fetching 24h volume {self.symbol}")

            data = requests.get(
                "https://api.binance.com/api/v3/ticker/24hr",
                params={"symbol": self.symbol},
                timeout=5
            ).json()
            volume = float(data["volume"])

            self.parent.after(0, lambda: self.safe_update(volume))
            log("VOLUME", f"Loaded 24h volume {volume:,.3f} {self.unit}")

        except Exception as e:
            log("VOLUME", f"Error {e}")

    def safe_update(self, volume):
        if getattr(self, "label", None) and self.label.winfo_exists():
            self.label.config(text=f"24h Volume : {volume:,.3f} {self.unit}")

    def stop(self):
        log("VOLUME", "Stopping (no loop running)")
