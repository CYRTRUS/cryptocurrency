"""
Components package for Crypto Dashboard
"""
from .ticker import CryptoTicker, BTCTicker
from .apps import MultiTickerApp, ToggleableTickerApp, fetch_initial_data

__all__ = ["CryptoTicker", "BTCTicker", "MultiTickerApp",
           "ToggleableTickerApp", "fetch_initial_data"]
__version__ = "1.0.0"
