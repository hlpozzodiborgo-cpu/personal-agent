"""
Service de récupération des actualités via NewsAPI.

NewsAPI (newsapi.org) :
- Gratuit jusqu'à 100 requêtes/jour (largement suffisant en usage personnel)
- Recherche par nom de société → fonctionne pour les ETF européens
- Clé à obtenir sur newsapi.org et à configurer dans Paramètres
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_newsapi_key_override: Optional[str] = None


class NewsService:

    @staticmethod
    def get_api_key() -> Optional[str]:
        global _newsapi_key_override
        if _newsapi_key_override:
            return _newsapi_key_override
        from config import NEWSAPI_KEY
        return NEWSAPI_KEY

    @staticmethod
    def set_api_key(key: str) -> None:
        global _newsapi_key_override
        _newsapi_key_override = key or None

    @staticmethod
    def get_news_for_portfolio(
        symbols: List[str],
        names: List[str],
        days: int = 3,
    ) -> List[Dict]:
        """
        Récupère les actualités récentes pour le portefeuille.

        Recherche par nom d'actif (plus fiable que le symbole pour les ETF EU).
        Fusionne et déduplique les articles, retourne les 20 plus récents.
        """
        api_key = NewsService.get_api_key()
        if not api_key:
            logger.warning("Clé NewsAPI absente — configurez-la dans Paramètres.")
            return []

        # Construire des termes de recherche à partir des noms
        # Ex: "iShares MSCI World Swap PEA UCITS ETF" → "iShares MSCI World"
        queries = []
        for name in names:
            # Garder les 3 premiers mots significatifs
            words = [w for w in name.split() if len(w) > 2 and w.upper() != w][:3]
            if words:
                queries.append(" ".join(words))

        # Ajouter les symboles US courts (sans suffixe de place boursière)
        for symbol in symbols:
            root = symbol.split(".")[0]
            if len(root) <= 5 and root not in [q.split()[0] for q in queries]:
                queries.append(root)

        # Dédupliquer et limiter les requêtes
        queries = list(dict.fromkeys(queries))[:6]

        all_articles: List[Dict] = []
        for query in queries:
            articles = NewsService._search(query, api_key, days)
            all_articles.extend(articles)

        # Dédupliquer par titre
        seen: set = set()
        unique: List[Dict] = []
        for a in all_articles:
            key = a["title"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(a)

        # Trier du plus récent au plus ancien, garder 20 max
        unique.sort(key=lambda x: x.get("date", ""), reverse=True)
        logger.info(f"NewsAPI: {len(unique)} articles pour {len(queries)} requêtes")
        return unique[:20]

    @staticmethod
    def _search(query: str, api_key: str, days: int = 3) -> List[Dict]:
        """Appel NewsAPI Everything endpoint."""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            r = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "from": from_date,
                    "pageSize": 5,
                    "apiKey": api_key,
                },
                headers={"User-Agent": "InvestorAI/1.0"},
                timeout=8,
            )
            if r.status_code == 401:
                logger.error("Clé NewsAPI invalide.")
                return []
            if r.status_code == 429:
                logger.warning("NewsAPI rate limit atteint.")
                return []
            if r.status_code != 200:
                logger.warning(f"NewsAPI {r.status_code} pour '{query}'")
                return []

            return [
                {
                    "title": a["title"],
                    "description": a.get("description") or "",
                    "source": a["source"]["name"],
                    "url": a["url"],
                    "date": a["publishedAt"][:10],
                    "query": query,
                }
                for a in r.json().get("articles", [])
                if a.get("title") and a["title"] != "[Removed]"
            ]
        except Exception as e:
            logger.error(f"NewsAPI error pour '{query}': {e}")
            return []
