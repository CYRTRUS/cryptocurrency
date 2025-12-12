"""
Components package for Crypto Dashboard
"""
from .ticker import CryptoTicker
from .apps import MultiTickerApp, ToggleableTickerApp

__all__ = ["CryptoTicker", "MultiTickerApp", "ToggleableTickerApp"]
__version__ = "1.0.0"
