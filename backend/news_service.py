"""
Service pour récupérer et gérer les actualités financières via Finnhub
Phase 2: Suivi des actualités et recommandations
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"


class NewsService:
    """Service pour récupérer les actualités des actifs"""

    @staticmethod
    def get_news_for_symbol(symbol: str, api_key: str) -> List[Dict]:
        """
        Récupère les actualités pour un symbole donné via Finnhub
        
        Args:
            symbol: Le symbole de l'actif (ex: AAPL)
            api_key: Clé API Finnhub
            
        Returns:
            Liste des actualités avec détails
        """
        if not api_key:
            logger.warning("❌ FINNHUB_API_KEY non configurée - impossible de récupérer les actualités")
            return []
        
        try:
            logger.info(f"📰 Récupération des actualités pour {symbol}...")
            
            r = requests.get(
                f"{FINNHUB_BASE_URL}/news",
                params={
                    "symbol": symbol,
                    "token": api_key,
                    "minId": 0  # Récupérer les actualités récentes
                },
                timeout=10
            )
            
            if r.status_code == 429:
                logger.warning(f"⚠️ Finnhub rate limit atteint pour {symbol}")
                return []
            
            if r.status_code != 200:
                logger.warning(f"⚠️ Erreur Finnhub {r.status_code} pour {symbol}")
                return []
            
            news_list = r.json()
            logger.info(f"✅ {len(news_list)} actualités trouvées pour {symbol}")
            return news_list
            
        except requests.Timeout:
            logger.warning(f"⏱️ Timeout Finnhub pour {symbol}")
            return []
        except Exception as e:
            logger.error(f"❌ Erreur récupération actualités {symbol}: {e}")
            return []

    @staticmethod
    def get_news_for_portfolio(symbols: List[str], api_key: str) -> List[Dict]:
        """
        Récupère les actualités pour tous les symboles du portefeuille
        
        Args:
            symbols: Liste des symboles du portefeuille
            api_key: Clé API Finnhub
            
        Returns:
            Liste combinée des actualités triées par date
        """
        import time
        all_news = []
        
        for i, symbol in enumerate(symbols):
            news = NewsService.get_news_for_symbol(symbol, api_key)
            
            # Ajouter le symbole associé à chaque actualité
            for article in news:
                article['symbol'] = symbol
                all_news.append(article)
            
            # Petit délai entre les requêtes pour éviter rate limit
            if i < len(symbols) - 1:
                time.sleep(0.1)
        
        logger.info(f"📰 Total: {len(all_news)} actualités trouvées pour {len(symbols)} symboles")
        
        # Trier par date décroissante (plus récent en premier)
        all_news.sort(
            key=lambda x: x.get('datetime', 0),
            reverse=True
        )
        
        return all_news

    @staticmethod
    def filter_recent_news(news_list: List[Dict], hours: int = 24) -> List[Dict]:
        """
        Filtre les actualités pour ne garder que les récentes
        
        Args:
            news_list: Liste des actualités
            hours: Nombre d'heures à considérer (par défaut 24h)
            
        Returns:
            Liste filtrée des actualités récentes
        """
        now = datetime.now().timestamp()
        cutoff = now - (hours * 3600)
        
        return [
            article for article in news_list
            if article.get('datetime', 0) >= cutoff
        ]

    @staticmethod
    def get_article_details(article: Dict) -> Dict:
        """
        Extrait les informations pertinentes d'un article
        
        Args:
            article: Données brutes de l'article depuis Finnhub
            
        Returns:
            Dictionnaire avec les informations formatées
        """
        timestamp = article.get('datetime', 0)
        date_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'symbol': article.get('symbol', ''),
            'title': article.get('headline', ''),
            'summary': article.get('summary', ''),
            'url': article.get('url', ''),
            'source': article.get('source', 'Unknown'),
            'published_at': date_time,
            'timestamp': timestamp,
            'image': article.get('image', None),
            'related': article.get('related', [])
        }
