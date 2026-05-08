"""
Application FastAPI principale - API REST pour l'agent Investor AI
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# ============ CONFIGURATION ============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import DATABASE_URL, DEBUG
from models import Base, Asset as AssetModel, Transaction as TransactionModel, AppSetting
from schemas import (
    AssetCreate, Asset, HoldingCreate, Holding,
    PortfolioStats, PortfolioDetailResponse, TransactionCreate
)
from crud import AssetCRUD, HoldingCRUD
from finance_service import FinanceService
# Phase 2: News & Recommendations
try:
    from routes_news import router as news_router
    logger.info("✅ Routes news & recommandations disponibles")
except ImportError as e:
    logger.warning(f"⚠️ Routes news non disponibles (routes_news.py): {e}")
    news_router = None

# Database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Migration: ajout de la colonne purchase_date si absente
from sqlalchemy import text
with engine.connect() as _conn:
    try:
        _conn.execute(text("ALTER TABLE holdings ADD COLUMN purchase_date DATETIME"))
        _conn.commit()
    except Exception:
        pass

# Charger la cle Finnhub depuis la DB (priorite sur le .env)
_startup_db = SessionLocal()
try:
    _setting = _startup_db.query(AppSetting).filter(AppSetting.key == "finnhub_api_key").first()
    if _setting and _setting.value:
        FinanceService.set_finnhub_key(_setting.value)
finally:
    _startup_db.close()

# FastAPI app
app = FastAPI(
    title="Investor AI API",
    description="API pour un agent IA analyste financier personnel",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ DEPENDENCY ============
def get_db():
    """Dependency pour obtenir la session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ ROUTES - HEALTH ============
@app.get("/health", tags=["Health"])
async def health_check():
    """Vérification de la santé de l'API"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "debug": DEBUG
    }


# ============ ROUTES - ASSETS ============
@app.get("/api/assets", tags=["Assets"], response_model=list[Asset])
async def list_assets(db: Session = Depends(get_db)):
    """Liste tous les actifs suivi"""
    assets = AssetCRUD.get_all(db)
    return assets


@app.post("/api/assets/add", tags=["Assets"], response_model=dict)
async def add_asset(symbol: str, name: str = None, asset_type: str = "stock", db: Session = Depends(get_db)):
    """
    Ajoute un nouvel actif à suivre
    
    - **symbol**: Symbole de l'actif (AAPL, BTC-USD, etc.)
    - **name**: Nom optionnel (sinon récupéré automatiquement)
    - **asset_type**: Type d'actif (stock, etf, crypto, bond)
    """
    try:
        # Récupère les infos de yfinance
        asset_info = FinanceService.get_asset_info(symbol)
        if not asset_info["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Impossible de trouver l'actif {symbol}"
            )
        
        # Crée ou récupère l'actif
        asset_name = name or asset_info.get("name", symbol)
        asset = AssetCRUD.get_or_create(db, symbol, asset_name, asset_type)
        
        # Met à jour le prix
        price = asset_info.get("current_price", 0)
        asset = AssetCRUD.update_price(db, symbol, price)
        
        return {
            "success": True,
            "asset_id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "current_price": asset.current_price
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout d'un actif: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/search", tags=["Assets"])
async def search_assets(q: str):
    """Recherche d'actifs par nom ou symbole via Yahoo Finance (actions, ETF, crypto…)"""
    import requests as req
    if len(q.strip()) < 2:
        return {"results": []}
    try:
        r = req.get(
            "https://query2.finance.yahoo.com/v1/finance/search",
            params={"q": q, "quotesCount": 10, "newsCount": 0},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        if r.status_code != 200:
            return {"results": []}
        type_map = {
            "EQUITY": "stock", "ETF": "etf", "MUTUALFUND": "etf",
            "CRYPTOCURRENCY": "crypto", "CURRENCY": "forex"
        }
        results = [
            {
                "symbol": q["symbol"],
                "display_symbol": q["symbol"],
                "name": q.get("longname") or q.get("shortname") or q["symbol"],
                "type": q.get("quoteType", ""),
                "asset_type": type_map.get(q.get("quoteType", ""), "stock"),
                "exchange": q.get("exchange", "")
            }
            for q in r.json().get("quotes", [])
            if q.get("symbol") and q.get("quoteType") != "FUTURE"
        ]
        return {"results": results}
    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        return {"results": []}


@app.get("/api/assets/{symbol}/info", tags=["Assets"])
async def get_asset_info(symbol: str):
    """Récupère les infos détaillées d'un actif"""
    try:
        info = FinanceService.get_asset_info(symbol)
        if not info["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Actif {symbol} non trouvé"
            )
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/assets/{symbol}/price-at", tags=["Assets"])
async def get_price_at_date(symbol: str, date: str):
    """Prix de cloture d'un actif a une date donnee (gere weekends et jours feries)"""
    price = FinanceService.get_price_at_date(symbol, date)
    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucun prix disponible pour {symbol} a la date {date}. Entrez le prix manuellement."
        )
    return {"symbol": symbol, "date": date, "price": round(price, 4)}


@app.get("/api/assets/{symbol}/history", tags=["Assets"])
async def get_asset_history(symbol: str, period: str = "1mo", interval: str = "1d"):
    """
    Récupère l'historique des prix d'un actif
    
    - **period**: Période (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y)
    - **interval**: Intervalle (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
    """
    try:
        history = FinanceService.get_historical_data(symbol, period, interval)
        return history
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ ROUTES - HOLDINGS (Positions) ============
@app.post("/api/holdings/add", tags=["Holdings"], response_model=dict)
async def add_holding(
    asset_id: int,
    quantity: float,
    purchase_date: str,
    price: float = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    try:
        asset = db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actif non trouve")

        purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")

        # Prix: fourni par l'utilisateur ou recupere depuis l'historique
        if price is None:
            price = FinanceService.get_price_at_date(asset.symbol, purchase_date)
            if price is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Prix introuvable pour {asset.symbol} a cette date. Entrez-le manuellement."
                )

        holding = HoldingCRUD.create(db, asset_id, quantity, price, notes, purchase_dt)

        # Enregistre la transaction a la date d'achat (sans modifier la position)
        transaction = TransactionModel(
            holding_id=holding.id,
            transaction_type="buy",
            quantity=quantity,
            price_per_unit=price,
            total_amount=quantity * price,
            notes=notes or "Position initiale",
            date=purchase_dt
        )
        db.add(transaction)
        db.commit()

        return {
            "success": True,
            "holding_id": holding.id,
            "asset": asset.symbol,
            "quantity": quantity,
            "price": price,
            "purchase_date": purchase_date,
            "total_invested": quantity * price
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur ajout position: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/portfolio", tags=["Portfolio"], response_model=dict)
async def get_portfolio_overview(db: Session = Depends(get_db)):
    """
    Récupère la vue d'ensemble du portefeuille
    
    Retourne:
    - Total investi et valeur actuelle
    - Gain/Perte en € et %
    - Liste de toutes les positions
    - Meilleur et pire actif
    """
    try:
        holdings = HoldingCRUD.get_all_active(db)
        
        if not holdings:
            return {
                "stats": {
                    "total_invested": 0,
                    "total_current_value": 0,
                    "total_gain_loss": 0,
                    "gain_loss_percent": 0,
                    "number_of_holdings": 0,
                    "last_updated": datetime.utcnow().isoformat()
                },
                "holdings": [],
                "top_gainer": None,
                "top_loser": None
            }
        
        # Prépare les données avec prix en temps réel
        holdings_data = []
        for holding in holdings:
            asset = holding.asset
            live_price = FinanceService.get_current_price(asset.symbol) or asset.current_price
            holdings_data.append({
                "id": holding.id,
                "symbol": asset.symbol,
                "name": asset.name,
                "quantity": holding.quantity,
                "avg_purchase_price": holding.avg_purchase_price,
                "current_price": live_price,
                "total_invested": holding.total_cost
            })
        
        # Calcule les stats
        stats = FinanceService.calculate_portfolio_stats(holdings_data)
        
        return {
            "stats": {
                "total_invested": stats["total_invested"],
                "total_current_value": stats["total_current_value"],
                "total_gain_loss": stats["total_gain_loss"],
                "gain_loss_percent": stats["total_gain_loss_percent"],
                "number_of_holdings": stats["number_of_holdings"],
                "last_updated": datetime.utcnow().isoformat()
            },
            "holdings": stats["holdings"],
            "top_gainer": stats["top_gainer"],
            "top_loser": stats["top_loser"]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/holdings/{holding_id}", tags=["Holdings"])
async def remove_holding(holding_id: int, db: Session = Depends(get_db)):
    """Supprime une position (la marque comme inactive)"""
    try:
        success = HoldingCRUD.delete(db, holding_id)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression d'une position: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position non trouvée"
        )
    return {"success": True, "message": "Position supprimée"}


# ============ SETTINGS ============
@app.get("/api/settings", tags=["Settings"])
async def get_settings():
    return {"finnhub_configured": bool(FinanceService.get_finnhub_key())}


@app.put("/api/settings/finnhub-key", tags=["Settings"])
async def update_finnhub_key(key: str, db: Session = Depends(get_db)):
    setting = db.query(AppSetting).filter(AppSetting.key == "finnhub_api_key").first()
    if setting:
        setting.value = key
    else:
        db.add(AppSetting(key="finnhub_api_key", value=key))
    db.commit()
    FinanceService.set_finnhub_key(key)
    return {"success": True}


@app.get("/api/settings/test-finnhub", tags=["Settings"])
async def test_finnhub_key():
    price = FinanceService._get_quote_finnhub("AAPL")
    if price:
        return {"success": True, "message": f"Cle valide — AAPL: ${price:.2f}"}
    return {"success": False, "message": "Cle invalide ou limite atteinte"}


# ============ PHASE 2 - NEWS & RECOMMENDATIONS ============
if news_router:
    app.include_router(news_router)
    logger.info("✅ Routes news & recommandations chargées")


# ============ ROOT ============
@app.get("/", tags=["Info"])
async def root():
    """Endpoint racine avec infos sur l'API"""
    return {
        "name": "Investor AI - Personal Financial Analyst",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running",
        "database": DATABASE_URL
    }


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Démarrage de l'API Investor AI...")
    print("📚 Docs disponibles à: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
