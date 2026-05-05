"""
Service pour récupérer les données financières en temps réel
Priorité: Finnhub (actions/ETF) → Yahoo Finance → Données mockées → Données générées
"""
import requests
import yfinance as yf
import logging
from datetime import datetime
from typing import Dict, Optional
import time

logger = logging.getLogger(__name__)

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# 🎯 CACHE EN MÉMOIRE: {symbol: {data, timestamp}}
PRICE_CACHE = {}
CACHE_EXPIRY_MINUTES = 10  # Rafraîchissement toutes les 10 minutes

# 📁 FALLBACK DONNÉES: quand Yahoo est down
MOCK_DATA = {
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "current_price": 150.25,
        "currency": "USD",
        "market_cap": 2.3e12,
        "pe_ratio": 28.5,
        "dividend_yield": 0.004,
        "52_week_high": 199.62,
        "52_week_low": 124.17,
        "source": "mock"
    },
    "BTC-USD": {
        "symbol": "BTC-USD",
        "name": "Bitcoin",
        "current_price": 42350.00,
        "currency": "USD",
        "market_cap": 8.3e11,
        "pe_ratio": None,
        "dividend_yield": 0.0,
        "52_week_high": 69045.00,
        "52_week_low": 21000.00,
        "source": "mock"
    },
    "VFV.TO": {
        "symbol": "VFV.TO",
        "name": "Vanguard U.S. Total Market Index ETF",
        "current_price": 38.95,
        "currency": "CAD",
        "market_cap": 2.1e9,
        "pe_ratio": 22.3,
        "dividend_yield": 0.018,
        "52_week_high": 41.25,
        "52_week_low": 33.50,
        "source": "mock"
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "current_price": 140.75,
        "currency": "USD",
        "market_cap": 1.87e12,
        "pe_ratio": 25.3,
        "dividend_yield": 0.0,
        "52_week_high": 188.52,
        "52_week_low": 102.21,
        "source": "mock"
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "current_price": 310.50,
        "currency": "USD",
        "market_cap": 2.31e12,
        "pe_ratio": 30.2,
        "dividend_yield": 0.007,
        "52_week_high": 365.75,
        "52_week_low": 215.34,
        "source": "mock"
    },
    "EUR=X": {
        "symbol": "EUR=X",
        "name": "EUR/USD Exchange Rate",
        "current_price": 1.0850,
        "currency": "USD",
        "market_cap": None,
        "pe_ratio": None,
        "dividend_yield": 0.0,
        "52_week_high": 1.1275,
        "52_week_low": 0.9535,
        "source": "mock"
    },
    "GBP=X": {
        "symbol": "GBP=X",
        "name": "GBP/USD Exchange Rate",
        "current_price": 1.2650,
        "currency": "USD",
        "market_cap": None,
        "pe_ratio": None,
        "dividend_yield": 0.0,
        "52_week_high": 1.3285,
        "52_week_low": 1.1758,
        "source": "mock"
    },
    "ETH-USD": {
        "symbol": "ETH-USD",
        "name": "Ethereum",
        "current_price": 2350.00,
        "currency": "USD",
        "market_cap": 2.82e11,
        "pe_ratio": None,
        "dividend_yield": 0.0,
        "52_week_high": 4891.70,
        "52_week_low": 883.25,
        "source": "mock"
    },
    "SPY": {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "current_price": 425.50,
        "currency": "USD",
        "market_cap": 4.2e11,
        "pe_ratio": 24.8,
        "dividend_yield": 0.015,
        "52_week_high": 476.93,
        "52_week_low": 371.51,
        "source": "mock"
    },
    "QQQ": {
        "symbol": "QQQ",
        "name": "Invesco QQQ Trust",
        "current_price": 380.25,
        "currency": "USD",
        "market_cap": 1.47e11,
        "pe_ratio": 31.5,
        "dividend_yield": 0.005,
        "52_week_high": 455.45,
        "52_week_low": 290.44,
        "source": "mock"
    },
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "current_price": 185.50,
        "currency": "USD",
        "market_cap": 5.86e11,
        "pe_ratio": 65.2,
        "dividend_yield": 0.0,
        "52_week_high": 299.29,
        "52_week_low": 138.80,
        "source": "mock"
    },
    "AMZN": {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "current_price": 175.75,
        "currency": "USD",
        "market_cap": 1.83e12,
        "pe_ratio": 48.5,
        "dividend_yield": 0.0,
        "52_week_high": 198.50,
        "52_week_low": 85.87,
        "source": "mock"
    }
}


class FinanceService:

    @staticmethod
    def _is_crypto(symbol: str) -> bool:
        """Les cryptos et devises ne sont pas supportées par Finnhub en tier gratuit"""
        return "-USD" in symbol or "-EUR" in symbol or "=X" in symbol

    @staticmethod
    def _get_quote_finnhub(symbol: str) -> Optional[float]:
        """Prix actuel depuis Finnhub (1 appel API, ~200ms)"""
        from config import FINNHUB_API_KEY
        if not FINNHUB_API_KEY:
            return None
        try:
            r = requests.get(
                f"{FINNHUB_BASE_URL}/quote",
                params={"symbol": symbol, "token": FINNHUB_API_KEY},
                timeout=5
            )
            if r.status_code == 429:
                logger.warning(f"⚠️ Finnhub rate limit pour {symbol} — bascule sur Yahoo")
                return None
            if r.status_code != 200:
                return None
            price = r.json().get("c", 0)
            return float(price) if price else None
        except Exception as e:
            logger.warning(f"⚠️ Finnhub quote échoué pour {symbol}: {e}")
            return None

    @staticmethod
    def _get_info_finnhub(symbol: str) -> Optional[Dict]:
        """Infos complètes depuis Finnhub (quote + profil, 2 appels API)"""
        from config import FINNHUB_API_KEY
        if not FINNHUB_API_KEY:
            return None
        try:
            r_quote = requests.get(
                f"{FINNHUB_BASE_URL}/quote",
                params={"symbol": symbol, "token": FINNHUB_API_KEY},
                timeout=5
            )
            if r_quote.status_code == 429:
                logger.warning(f"⚠️ Finnhub rate limit pour {symbol} — bascule sur Yahoo")
                return None
            if r_quote.status_code != 200:
                return None
            price = r_quote.json().get("c", 0)
            if not price:
                return None

            name = symbol
            try:
                r_profile = requests.get(
                    f"{FINNHUB_BASE_URL}/stock/profile2",
                    params={"symbol": symbol, "token": FINNHUB_API_KEY},
                    timeout=5
                )
                if r_profile.status_code == 200:
                    name = r_profile.json().get("name", symbol) or symbol
            except Exception:
                pass

            return {
                "symbol": symbol,
                "name": name,
                "current_price": float(price),
                "currency": "USD",
                "success": True,
                "source": "finnhub"
            }
        except Exception as e:
            logger.warning(f"⚠️ Finnhub info échoué pour {symbol}: {e}")
            return None

    @staticmethod
    def _generate_default_data(symbol: str) -> Dict:
        """Génère des données par défaut quand rien n'est disponible"""
        import random
        
        # Estimer le prix basé sur le type de symbole
        if symbol.endswith("-USD") or "=" in symbol:  # Crypto ou devise
            base_price = random.uniform(100, 50000)
        else:  # Action/ETF
            base_price = random.uniform(50, 500)
        
        return {
            "symbol": symbol,
            "name": f"{symbol} (Données par défaut)",
            "current_price": base_price,
            "currency": "USD",
            "market_cap": None,
            "pe_ratio": None,
            "dividend_yield": 0.0,
            "52_week_high": base_price * 1.3,
            "52_week_low": base_price * 0.7,
            "success": True,
            "source": "generated"  # Important pour le debugg
        }
    
    
    @staticmethod
    def _is_cache_valid(symbol: str) -> bool:
        if symbol not in PRICE_CACHE:
            return False
        age_min = (datetime.now() - PRICE_CACHE[symbol]["timestamp"]).total_seconds() / 60
        return age_min < CACHE_EXPIRY_MINUTES
    
    @staticmethod
    def _get_from_cache(symbol: str) -> Optional[Dict]:
        """Récupère les données du cache si valides"""
        if FinanceService._is_cache_valid(symbol):
            logger.info(f"✅ Cache utilisé pour {symbol}")
            return PRICE_CACHE[symbol]["data"]
        return None
    
    @staticmethod
    def _save_to_cache(symbol: str, data: Dict) -> None:
        """Sauvegarde les données en cache"""
        PRICE_CACHE[symbol] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    @staticmethod
    def get_asset_info(symbol: str) -> Dict:
        """
        Priorité: Cache → Finnhub (actions/ETF) → Yahoo Finance → Mock → Généré
        Retourne toujours quelque chose.
        """
        cached = FinanceService._get_from_cache(symbol)
        if cached:
            return cached

        # Finnhub (sauf crypto/devises non supportées en free tier)
        if not FinanceService._is_crypto(symbol):
            logger.info(f"📊 Finnhub: récupération infos pour {symbol}...")
            result = FinanceService._get_info_finnhub(symbol)
            if result:
                FinanceService._save_to_cache(symbol, result)
                return result

        # Yahoo Finance (fallback ou crypto)
        try:
            time.sleep(0.5)
            logger.info(f"📊 Yahoo: récupération infos pour {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            result = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "current_price": info.get("currentPrice", 0),
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "dividend_yield": info.get("dividendYield", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "success": True,
                "source": "yahoo"
            }
            FinanceService._save_to_cache(symbol, result)
            return result
        except Exception as e:
            logger.warning(f"⚠️ Yahoo échoué pour {symbol}: {e}")

        # Données mockées pré-définies
        if symbol in MOCK_DATA:
            mock_result = MOCK_DATA[symbol].copy()
            mock_result["success"] = True
            FinanceService._save_to_cache(symbol, mock_result)
            return mock_result

        # Données générées (dernier recours)
        generated = FinanceService._generate_default_data(symbol)
        FinanceService._save_to_cache(symbol, generated)
        return generated
    
    
    @staticmethod
    def get_current_price(symbol: str) -> Optional[float]:
        """
        Priorité: Cache → Finnhub (actions/ETF) → Yahoo Finance → Mock → Généré
        """
        cached = FinanceService._get_from_cache(symbol)
        if cached:
            return cached.get("current_price")

        # Finnhub (sauf crypto/devises)
        if not FinanceService._is_crypto(symbol):
            price = FinanceService._get_quote_finnhub(symbol)
            if price:
                FinanceService._save_to_cache(symbol, {
                    "current_price": price, "symbol": symbol, "source": "finnhub"
                })
                return price

        # Yahoo Finance (fallback ou crypto)
        try:
            time.sleep(0.5)
            ticker = yf.Ticker(symbol)
            price = ticker.info.get("currentPrice")
            if price:
                FinanceService._save_to_cache(symbol, {
                    "current_price": float(price), "symbol": symbol, "source": "yahoo"
                })
                return float(price)
        except Exception as e:
            logger.warning(f"⚠️ Yahoo prix échoué pour {symbol}: {e}")

        if symbol in MOCK_DATA:
            return MOCK_DATA[symbol].get("current_price")

        return FinanceService._generate_default_data(symbol).get("current_price", 100.0)
    
    
    @staticmethod
    def get_price_at_date(symbol: str, date_str: str) -> Optional[float]:
        """Prix de cloture d'un actif a une date donnee via Yahoo Finance chart API.
        Retourne le dernier jour de trading <= date (gere weekends et jours feries)."""
        try:
            from datetime import timedelta
            target = datetime.strptime(date_str, "%Y-%m-%d")
            ts_from = int((target - timedelta(days=7)).timestamp())
            ts_to = int((target + timedelta(days=1)).timestamp())

            r = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                params={"period1": ts_from, "period2": ts_to, "interval": "1d"},
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                timeout=10
            )
            if r.status_code != 200:
                return None

            result = r.json().get("chart", {}).get("result")
            if not result:
                return None

            timestamps = result[0].get("timestamp", [])
            closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])

            if not timestamps or not closes:
                return None

            # Dernier jour de trading <= date cible
            target_ts = int(target.timestamp()) + 86400
            pairs = [(ts, c) for ts, c in zip(timestamps, closes) if ts <= target_ts and c is not None]
            if not pairs:
                return None
            return float(pairs[-1][1])
        except Exception as e:
            logger.error(f"Erreur prix historique {symbol} @ {date_str}: {e}")
            return None

    @staticmethod
    def get_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict:
        """
        Récupère les données historiques d'un actif
        
        Args:
            symbol: Symbole de l'actif
            period: Période ('1d', '5d', '1mo', '3mo', '6mo', '1y', '5y')
            interval: Intervalle ('1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo')
        
        Returns:
            Dict avec historique des prix
        """
        try:
            time.sleep(2)
            print(f"📈 Récupération de l'historique {period} pour {symbol}...")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return {"symbol": symbol, "data": [], "success": False}
            
            # Convertir en format exploitable
            history = []
            for date, row in data.iterrows():
                history.append({
                    "date": date.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            return {
                "symbol": symbol,
                "data": history,
                "success": True,
                "source": "yahoo"
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique de {symbol}: {e}")
            return {"symbol": symbol, "data": [], "success": False, "error": str(e)}
    
    @staticmethod
    def calculate_portfolio_stats(holdings_data: list) -> Dict:
        """
        Calcule les statistiques du portefeuille
        
        Args:
            holdings_data: Liste des positions avec current_price et quantity
        
        Returns:
            Dict avec statistiques
        """
        total_invested = 0
        total_current_value = 0
        holdings_stats = []
        
        for holding in holdings_data:
            quantity = holding["quantity"]
            avg_price = holding["avg_purchase_price"]
            current_price = holding["current_price"]
            
            invested = quantity * avg_price
            current_value = quantity * current_price
            gain_loss = current_value - invested
            gain_loss_percent = (gain_loss / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_current_value += current_value
            
            holdings_stats.append({
                "id": holding.get("id"),  # 🔑 Inclure l'ID pour la suppression frontend
                "symbol": holding["symbol"],
                "name": holding["name"],
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "invested": invested,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_percent": gain_loss_percent
            })
        
        total_gain_loss = total_current_value - total_invested
        total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Top gainer et loser
        top_gainer = max(holdings_stats, key=lambda x: x["gain_loss_percent"]) if holdings_stats else None
        top_loser = min(holdings_stats, key=lambda x: x["gain_loss_percent"]) if holdings_stats else None
        
        return {
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "holdings": holdings_stats,
            "top_gainer": top_gainer,
            "top_loser": top_loser,
            "number_of_holdings": len(holdings_stats)
        }
