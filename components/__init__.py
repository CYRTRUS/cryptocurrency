"""
Components package for Crypto Dashboard
"""
from .ticker import CryptoTicker
from .apps import MultiTickerApp, ToggleableTickerApp, fetch_initial_data

__all__ = ["CryptoTicker", "MultiTickerApp",
           "ToggleableTickerApp", "fetch_initial_data"]
__version__ = "1.0.0"
