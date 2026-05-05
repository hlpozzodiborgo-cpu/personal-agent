"""
Service pour récupérer les données financières en temps réel
"""
import yfinance as yf
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio
import time

logger = logging.getLogger(__name__)


class FinanceService:
    """Service pour récupérer les données financières"""
    
    @staticmethod
    def get_asset_info(symbol: str) -> Dict:
        """
        Récupère les informations d'un actif
        
        Args:
            symbol: Symbole de l'actif (ex: AAPL, BTC-USD)
        
        Returns:
            Dict avec les infos de l'actif
        """
        try:
            time.sleep(3)  # Délai 3 secondes entre chaque requête (anti rate-limit)
            print(f"📊 Récupération des infos pour {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "current_price": info.get("currentPrice", 0),
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "dividend_yield": info.get("dividendYield", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "success": True
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos de {symbol}: {e}")
            return {
                "symbol": symbol,
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_current_price(symbol: str) -> Optional[float]:
        """
        Récupère le prix actuel d'un actif
        
        Args:
            symbol: Symbole de l'actif
        
        Returns:
            Prix actuel ou None
        """
        try:
            time.sleep(3)  # Délai 3 secondes anti rate-limit
            ticker = yf.Ticker(symbol)
            price = ticker.info.get("currentPrice")
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du prix de {symbol}: {e}")
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
            time.sleep(3)  # Délai 3 secondes anti rate-limit
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
                "success": True
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
