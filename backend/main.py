"""
Application FastAPI principale - API REST pour l'agent Investor AI
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

from config import DATABASE_URL, DEBUG
from models import Base, Asset as AssetModel
from schemas import (
    AssetCreate, Asset, HoldingCreate, Holding, 
    PortfolioStats, PortfolioDetailResponse, TransactionCreate
)
from crud import AssetCRUD, HoldingCRUD, TransactionCRUD, PriceHistoryCRUD
from finance_service import FinanceService

# ============ CONFIGURATION ============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

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
    avgPrice: float,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """
    Ajoute une nouvelle position au portefeuille
    
    Enregistre:
    1. La position (nombre de parts + prix moyen)
    2. Une transaction d'achat
    """
    try:
        holding = HoldingCRUD.create(db, asset_id, quantity, avgPrice, notes)
        
        # Enregistre la transaction
        TransactionCRUD.create(
            db, holding.id, "buy", quantity, avgPrice,
            notes="Position initiale" if not notes else notes
        )
        
        asset = db.query(AssetModel).filter(AssetModel.id == asset_id).first()
        
        return {
            "success": True,
            "holding_id": holding.id,
            "asset": asset.symbol,
            "quantity": holding.quantity,
            "total_invested": holding.total_cost
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout d'une position: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
        
        # Prépare les données
        holdings_data = []
        for holding in holdings:
            asset = holding.asset
            holdings_data.append({
                "id": holding.id,
                "symbol": asset.symbol,
                "name": asset.name,
                "quantity": holding.quantity,
                "avg_purchase_price": holding.avg_purchase_price,
                "current_price": asset.current_price,
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
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position non trouvée"
            )
        return {"success": True, "message": "Position supprimée"}
    except Exception as e:
        logger.error(f"Erreur lors de la suppression d'une position: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
