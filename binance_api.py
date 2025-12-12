import requests


def get_current_price(symbol):
    """Get current price and 24h stats via REST API."""
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol.upper()}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            'price': float(data['lastPrice']),
            'change': float(data['priceChange']),
            'percent': float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None
