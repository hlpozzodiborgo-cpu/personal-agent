"""
Routes Phase 2 : Actualités & Recommandations IA

Flux :
  1. Le frontend déclenche GET /api/news/analyze
  2. On lit le portefeuille actif depuis la DB
  3. On récupère les actualités via NewsAPI (par nom d'actif)
  4. On envoie les articles + le contexte du portefeuille à Claude
  5. Claude retourne une analyse structurée en JSON
  6. On renvoie le résultat au frontend
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from config import DATABASE_URL
from crud import HoldingCRUD
from finance_service import FinanceService
from news_service import NewsService
from ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["News & AI"])

_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
_Session = sessionmaker(bind=_engine)

def get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


@router.get("/analyze")
async def analyze_portfolio_news(
    days: int = 3,
    db: Session = Depends(get_db),
):
    """
    Analyse IA des actualités pour le portefeuille.

    - Lit les positions actives depuis la DB
    - Cherche les actualités récentes via NewsAPI
    - Envoie à Claude pour analyse
    - Retourne : résumé marché + analyse par article
    """
    holdings = HoldingCRUD.get_all_active(db)
    if not holdings:
        raise HTTPException(status_code=404, detail="Aucune position dans le portefeuille.")

    # Construire le contexte portefeuille pour Claude
    holdings_ctx = []
    symbols, names = [], []
    for h in holdings:
        asset = h.asset
        live_price = FinanceService.get_current_price(asset.symbol) or asset.current_price
        gain_pct = ((live_price - h.avg_purchase_price) / h.avg_purchase_price * 100) if h.avg_purchase_price else 0
        holdings_ctx.append({
            "symbol":        asset.symbol,
            "name":          asset.name,
            "quantity":      h.quantity,
            "avg_price":     h.avg_purchase_price,
            "current_price": live_price,
            "gain_pct":      round(gain_pct, 1),
        })
        if asset.symbol not in symbols:
            symbols.append(asset.symbol)
            names.append(asset.name)

    logger.info(f"Analyse pour {len(symbols)} actifs : {symbols}")

    # Récupérer les actualités
    articles = NewsService.get_news_for_portfolio(symbols, names, days=days)
    if not articles:
        return {
            "market_summary": "Aucune actualité récente trouvée. Vérifiez votre clé NewsAPI dans Paramètres.",
            "articles": [],
            "holdings_count": len(holdings_ctx),
        }

    # Analyse Claude
    result = AIService.analyze_news_for_portfolio(articles, holdings_ctx)

    # Enrichir les articles analysés avec les données brutes (titre, url, source)
    article_map = {i + 1: a for i, a in enumerate(articles)}
    for item in result.get("articles", []):
        idx = item.get("index", 0)
        raw = article_map.get(idx, {})
        item["title"]  = raw.get("title", "")
        item["url"]    = raw.get("url", "")
        item["source"] = raw.get("source", "")
        item["date"]   = raw.get("date", "")

    result["holdings_count"] = len(holdings_ctx)
    result["articles_fetched"] = len(articles)
    return result


@router.get("/status")
async def get_news_status():
    """Vérifie quelles clés API sont configurées."""
    return {
        "newsapi_configured":    bool(NewsService.get_api_key()),
        "anthropic_configured":  bool(AIService.get_api_key()),
    }
