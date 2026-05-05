"""
Données mockées pour tests quand Yahoo Finance est bloqué (429)
"""

MOCK_PRICES = {
    "AAPL": 150.25,
    "BTC-USD": 42350.00,
    "VFV.TO": 38.95,
    "MSFT": 310.50,
    "GOOGL": 140.75,
}

MOCK_ASSET_INFO = {
    "AAPL": {
        "currentPrice": 150.25,
        "currency": "USD",
        "fiftyTwoWeekHigh": 199.62,
        "fiftyTwoWeekLow": 124.17,
        "marketCap": 2.3e12,
        "trailingPE": 28.5,
        "dividendYield": 0.004,
    },
    "BTC-USD": {
        "currentPrice": 42350.00,
        "currency": "USD",
        "fiftyTwoWeekHigh": 69045.00,
        "fiftyTwoWeekLow": 21000.00,
        "marketCap": 8.3e11,
        "trailingPE": None,
        "dividendYield": 0.0,
    },
    "VFV.TO": {
        "currentPrice": 38.95,
        "currency": "CAD",
        "fiftyTwoWeekHigh": 41.25,
        "fiftyTwoWeekLow": 33.50,
        "marketCap": 2.1e9,
        "trailingPE": 22.3,
        "dividendYield": 0.018,
    },
}

MOCK_HISTORICAL = {
    "AAPL": {
        "Close": [145.0, 146.5, 148.0, 149.5, 150.25],
        "Open": [144.5, 145.8, 147.2, 148.8, 149.5],
        "High": [148.0, 149.0, 150.5, 151.0, 152.0],
        "Low": [143.5, 145.0, 146.8, 148.0, 148.5],
    }
}

def get_mock_price(symbol):
    """Retourner prix mockié pour tester"""
    return MOCK_PRICES.get(symbol, 100.0)

def get_mock_info(symbol):
    """Retourner infos mockiées pour tester"""
    return MOCK_ASSET_INFO.get(symbol, {
        "currentPrice": 100.0,
        "currency": "USD",
        "fiftyTwoWeekHigh": 120.0,
        "fiftyTwoWeekLow": 80.0,
        "marketCap": 1e9,
        "trailingPE": 20.0,
        "dividendYield": 0.02,
    })
