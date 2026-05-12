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
from models import Base, Asset as AssetModel, Holding as HoldingModel, Transaction as TransactionModel, AppSetting
from schemas import (
    AssetCreate, Asset, HoldingCreate, Holding,
    PortfolioStats, PortfolioDetailResponse, TransactionCreate
)
from crud import AssetCRUD, HoldingCRUD
from finance_service import FinanceService
from ai_service import AIService
from news_service import NewsService
from routes_news import router as news_router
from agent.router import router as agent_router
from agent.models import AgentBase

# Database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
AgentBase.metadata.create_all(bind=engine)   # agent tables — does not touch Phase 1 tables

# Migration: ajout de la colonne purchase_date si absente
from sqlalchemy import text
with engine.connect() as _conn:
    try:
        _conn.execute(text("ALTER TABLE holdings ADD COLUMN purchase_date DATETIME"))
        _conn.commit()
    except Exception:
        pass
    try:
        _conn.execute(text("ALTER TABLE raw_articles ADD COLUMN processed_at DATETIME"))
        _conn.commit()
    except Exception:
        pass

# Charger toutes les cles API depuis la DB (priorite sur le .env)
_startup_db = SessionLocal()
try:
    for _key, _setter in [
        ("finnhub_api_key",   FinanceService.set_finnhub_key),
        ("anthropic_api_key", AIService.set_api_key),
        ("newsapi_key",       NewsService.set_api_key),
        ("gemini_api_key",    AIService.set_gemini_key),
        ("groq_api_key",      AIService.set_groq_key),
        ("ai_provider",       AIService.set_provider),
    ]:
        _s = _startup_db.query(AppSetting).filter(AppSetting.key == _key).first()
        if _s and _s.value:
            _setter(_s.value)
finally:
    _startup_db.close()

# FastAPI app
app = FastAPI(
    title="Investor AI API",
    description="API pour un agent IA analyste financier personnel",
    version="2.0.0"
)
app.include_router(news_router)
app.include_router(agent_router)

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


@app.get("/api/assets/{symbol}/price-history", tags=["Assets"])
async def get_asset_price_history(symbol: str, period: str = "1mo"):
    """Prix historiques bruts d'un symbole (pour comparaison de courbes)"""
    import requests as req
    from datetime import datetime, timedelta
    period_cfg = {
        "1d":  (timedelta(days=2),    "1d"),   # veille + aujourd'hui comme reference
        "1w":  (timedelta(weeks=1),   "1d"),
        "1mo": (timedelta(days=30),   "1d"),
        "1y":  (timedelta(days=365),  "1d"),
        "all": (timedelta(days=1825), "1d"),
    }
    delta, interval = period_cfg.get(period, (timedelta(days=30), "1d"))
    now = datetime.now()
    start_ts = int((now - delta).timestamp())
    is_intraday = interval in ("5m", "1h")
    try:
        r = req.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            params={"period1": start_ts, "period2": int(now.timestamp()), "interval": interval},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        if r.status_code != 200:
            raise HTTPException(status_code=404, detail=f"{symbol} non trouve")
        result = r.json().get("chart", {}).get("result")
        if not result:
            raise HTTPException(status_code=404, detail=f"Pas de donnees pour {symbol}")
        timestamps = result[0].get("timestamp", [])
        closes = result[0]["indicators"]["quote"][0].get("close", [])
        data = [
            {"date": datetime.fromtimestamp(ts).isoformat() if is_intraday else datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
             "value": price}
            for ts, price in zip(timestamps, closes) if price is not None
        ]
        return {"symbol": symbol, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/history", tags=["Portfolio"])
async def get_portfolio_history(period: str = "1mo", db: Session = Depends(get_db)):
    """Valeur historique du portefeuille reconstituee jour par jour"""
    import requests as req

    holdings = HoldingCRUD.get_all_active(db)
    if not holdings:
        return {"data": [], "order_dates": []}

    now = datetime.now()
    period_cfg = {
        "1d":  (now - __import__('datetime').timedelta(days=1),   "5m"),
        "1w":  (now - __import__('datetime').timedelta(weeks=1),  "1h"),
        "1mo": (now - __import__('datetime').timedelta(days=30),  "1h"),
        "1y":  (now - __import__('datetime').timedelta(days=365), "1d"),
        "all": (None,                                             "1d"),
    }
    start_dt, interval = period_cfg.get(period, period_cfg["1mo"])

    if start_dt is None:
        valid_dates = [h.purchase_date for h in holdings if h.purchase_date]
        if not valid_dates:
            return {"data": [], "order_dates": []}
        start_dt = min(valid_dates)

    start_ts = int(start_dt.timestamp())
    end_ts   = int(now.timestamp())
    is_intraday = interval in ("5m", "1h")

    # Prix historiques par symbole : {symbol: {timestamp: price}}
    unique_symbols = list(set(h.asset.symbol for h in holdings))
    symbol_prices = {}
    for symbol in unique_symbols:
        try:
            r = req.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                params={"period1": start_ts, "period2": end_ts, "interval": interval},
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                timeout=10
            )
            if r.status_code != 200:
                continue
            result = r.json().get("chart", {}).get("result")
            if not result:
                continue
            timestamps = result[0].get("timestamp", [])
            closes = result[0]["indicators"]["quote"][0].get("close", [])
            symbol_prices[symbol] = {
                ts: price for ts, price in zip(timestamps, closes) if price is not None
            }
        except Exception as e:
            logger.error(f"History error {symbol}: {e}")

    if not symbol_prices:
        return {"data": [], "order_dates": []}

    # Forward-fill : reporter le dernier prix connu sur les timestamps manquants.
    # Nécessaire quand le portefeuille mixe des actifs de marchés différents
    # (ex: ETF Euronext + action NYSE) qui ont des jours fériés distincts.
    all_timestamps_sorted = sorted(set(ts for prices in symbol_prices.values() for ts in prices))
    for symbol in symbol_prices:
        last_price = None
        for ts in all_timestamps_sorted:
            if ts in symbol_prices[symbol]:
                last_price = symbol_prices[symbol][ts]
            elif last_price is not None:
                symbol_prices[symbol][ts] = last_price

    # Reconstruction jour par jour avec TWR (Time-Weighted Return)
    # Le TWR elimine l'effet des depot/retraits pour comparer equitablement
    # avec d'autres actifs. Standard industrie (CFA Institute).
    all_timestamps = all_timestamps_sorted
    data = []
    twr_factor = 1.0
    prev_total = None  # Valeur totale au timestamp precedent (avec tous les ordres actifs)

    for ts in all_timestamps:
        dt = datetime.fromtimestamp(ts)
        date_str = dt.isoformat() if is_intraday else dt.strftime("%Y-%m-%d")
        current_d = dt.date()

        current_total = 0.0  # Tous les ordres actifs aujourd'hui (y compris nouveaux)
        old_total = 0.0      # Ordres actifs AVANT aujourd'hui (exclut depots du jour)

        for holding in holdings:
            if not holding.purchase_date:
                continue
            price = symbol_prices.get(holding.asset.symbol, {}).get(ts)
            if not price:
                continue
            purchase_d = holding.purchase_date.date()
            if purchase_d <= current_d:
                current_total += holding.quantity * price
            if purchase_d < current_d:
                old_total += holding.quantity * price

        if current_total <= 0:
            continue

        if prev_total is None or prev_total <= 0:
            twr_factor = 1.0          # Initialisation
        elif old_total > 0:
            twr_factor *= (old_total / prev_total)  # Rendement du jour hors depot

        prev_total = current_total
        data.append({"date": date_str, "value": round(current_total, 2), "twr": round(twr_factor * 100, 2)})

    # Dates d'ordres dans la periode (pas pour intraday)
    order_dates = [] if is_intraday else sorted(set(
        h.purchase_date.strftime("%Y-%m-%d")
        for h in holdings
        if h.purchase_date and h.purchase_date.timestamp() >= start_ts
    ))

    # Capital total investi (somme de tous les achats)
    total_invested = round(sum(h.total_cost for h in holdings), 2)

    return {"data": data, "order_dates": order_dates, "total_invested": total_invested}


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
                "total_invested": holding.total_cost,
                "purchase_date": holding.purchase_date.strftime("%Y-%m-%d") if holding.purchase_date else None,
                "notes": holding.notes
            })
        
        # Calcule les stats
        stats = FinanceService.calculate_portfolio_stats(holdings_data)
        
        return {
            "stats": {
                "total_invested": stats["total_invested"],
                "total_current_value": stats["total_current_value"],
                "total_gain_loss": stats["total_gain_loss"],
                "gain_loss_percent": stats["total_gain_loss_percent"],
                "number_of_holdings": len(set(h["symbol"] for h in holdings_data)),
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


@app.put("/api/holdings/{holding_id}", tags=["Holdings"])
async def update_holding(
    holding_id: int,
    quantity: float,
    purchase_date: str,
    price: float,
    notes: str = None,
    db: Session = Depends(get_db)
):
    holding = db.query(HoldingModel).filter(
        HoldingModel.id == holding_id, HoldingModel.is_active == True
    ).first()
    if not holding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position non trouvee")
    try:
        purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")
        holding.quantity = quantity
        holding.avg_purchase_price = price
        holding.total_cost = quantity * price
        holding.purchase_date = purchase_dt
        holding.notes = notes
        transaction = db.query(TransactionModel).filter(
            TransactionModel.holding_id == holding_id
        ).first()
        if transaction:
            transaction.quantity = quantity
            transaction.price_per_unit = price
            transaction.total_amount = quantity * price
            transaction.date = purchase_dt
            transaction.notes = notes or "Position initiale"
        db.commit()
        return {"success": True}
    except Exception as e:
        logger.error(f"Erreur modification position: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
def _is_real_key(value) -> bool:
    """Verifie qu'une cle est reelle (non vide, non placeholder)."""
    if not value:
        return False
    s = str(value).strip()
    return bool(s) and not s.lower().startswith("votre_") and s != ""


def _save_setting(db: Session, key: str, value: str):
    s = db.query(AppSetting).filter(AppSetting.key == key).first()
    if s:
        s.value = value
    else:
        db.add(AppSetting(key=key, value=value))
    db.commit()


def _delete_setting(db: Session, key: str, setter):
    s = db.query(AppSetting).filter(AppSetting.key == key).first()
    if s:
        s.value = None
        db.commit()
    setter("")


@app.get("/api/settings", tags=["Settings"])
async def get_settings():
    return {
        "finnhub_configured":   _is_real_key(FinanceService.get_finnhub_key()),
        "anthropic_configured": _is_real_key(AIService.get_api_key()),
        "newsapi_configured":   _is_real_key(NewsService.get_api_key()),
        "gemini_configured":    _is_real_key(AIService.get_gemini_key()),
        "groq_configured":      _is_real_key(AIService.get_groq_key()),
        "ai_provider":          AIService.get_provider(),
    }


@app.put("/api/settings/finnhub-key", tags=["Settings"])
async def update_finnhub_key(key: str, db: Session = Depends(get_db)):
    _save_setting(db, "finnhub_api_key", key)
    FinanceService.set_finnhub_key(key)
    return {"success": True}

@app.delete("/api/settings/finnhub-key", tags=["Settings"])
async def delete_finnhub_key(db: Session = Depends(get_db)):
    _delete_setting(db, "finnhub_api_key", FinanceService.set_finnhub_key)
    return {"success": True}


@app.put("/api/settings/anthropic-key", tags=["Settings"])
async def update_anthropic_key(key: str, db: Session = Depends(get_db)):
    _save_setting(db, "anthropic_api_key", key)
    AIService.set_api_key(key)
    return {"success": True}

@app.delete("/api/settings/anthropic-key", tags=["Settings"])
async def delete_anthropic_key(db: Session = Depends(get_db)):
    _delete_setting(db, "anthropic_api_key", AIService.set_api_key)
    return {"success": True}


@app.put("/api/settings/newsapi-key", tags=["Settings"])
async def update_newsapi_key(key: str, db: Session = Depends(get_db)):
    _save_setting(db, "newsapi_key", key)
    NewsService.set_api_key(key)
    return {"success": True}

@app.delete("/api/settings/newsapi-key", tags=["Settings"])
async def delete_newsapi_key(db: Session = Depends(get_db)):
    _delete_setting(db, "newsapi_key", NewsService.set_api_key)
    return {"success": True}


@app.get("/api/settings/test-finnhub", tags=["Settings"])
async def test_finnhub_key():
    price = FinanceService._get_quote_finnhub("AAPL")
    if price:
        return {"success": True, "message": f"Connexion Finnhub OK — AAPL: ${price:.2f}"}
    return {"success": False, "message": "Cle invalide ou rate limit atteint"}

@app.get("/api/settings/test-anthropic", tags=["Settings"])
async def test_anthropic_key():
    if not _is_real_key(AIService.get_api_key()):
        return {"success": False, "message": "Cle non configuree"}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=AIService.get_api_key())
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=8,
            messages=[{"role": "user", "content": "Reply: OK"}]
        )
        return {"success": True, "message": f"Claude connecte ({resp.model.split('-')[1]})"}
    except Exception as e:
        return {"success": False, "message": str(e)[:120]}

@app.get("/api/settings/masked-key/{key_name}", tags=["Settings"])
async def get_masked_key(key_name: str, db: Session = Depends(get_db)):
    """Retourne les premiers et derniers caracteres d'une cle sauvegardee."""
    allowed = {"finnhub_api_key", "anthropic_api_key", "newsapi_key", "gemini_api_key", "groq_api_key"}
    if key_name not in allowed:
        raise HTTPException(status_code=400, detail="Cle inconnue")
    s = db.query(AppSetting).filter(AppSetting.key == key_name).first()
    if not s or not s.value or not _is_real_key(s.value):
        return {"masked": None}
    v = s.value
    masked = (v[:6] + "..." + v[-4:]) if len(v) > 10 else "****"
    return {"masked": masked}


@app.put("/api/settings/ai-provider", tags=["Settings"])
async def set_ai_provider(provider: str, db: Session = Depends(get_db)):
    if provider not in {"claude", "gemini", "groq"}:
        raise HTTPException(status_code=400, detail="Fournisseur invalide")
    _save_setting(db, "ai_provider", provider)
    AIService.set_provider(provider)
    return {"success": True, "provider": provider}


@app.put("/api/settings/gemini-key", tags=["Settings"])
async def update_gemini_key(key: str, db: Session = Depends(get_db)):
    _save_setting(db, "gemini_api_key", key)
    AIService.set_gemini_key(key)
    return {"success": True}

@app.delete("/api/settings/gemini-key", tags=["Settings"])
async def delete_gemini_key(db: Session = Depends(get_db)):
    _delete_setting(db, "gemini_api_key", AIService.set_gemini_key)
    return {"success": True}


@app.put("/api/settings/groq-key", tags=["Settings"])
async def update_groq_key(key: str, db: Session = Depends(get_db)):
    _save_setting(db, "groq_api_key", key)
    AIService.set_groq_key(key)
    return {"success": True}

@app.delete("/api/settings/groq-key", tags=["Settings"])
async def delete_groq_key(db: Session = Depends(get_db)):
    _delete_setting(db, "groq_api_key", AIService.set_groq_key)
    return {"success": True}


@app.get("/api/settings/test-gemini", tags=["Settings"])
async def test_gemini_key():
    result = AIService.test_gemini()
    return result

@app.get("/api/settings/test-groq", tags=["Settings"])
async def test_groq_key():
    result = AIService.test_groq()
    return result


@app.get("/api/settings/test-newsapi", tags=["Settings"])
async def test_newsapi_key():
    if not _is_real_key(NewsService.get_api_key()):
        return {"success": False, "message": "Cle non configuree"}
    try:
        import requests as req
        r = req.get("https://newsapi.org/v2/everything",
                    params={"q": "market", "pageSize": 1, "apiKey": NewsService.get_api_key()},
                    timeout=5)
        if r.status_code == 200:
            n = r.json().get("totalResults", 0)
            return {"success": True, "message": f"NewsAPI OK — {n:,} articles indexés"}
        if r.status_code == 401:
            return {"success": False, "message": "Cle invalide"}
        return {"success": False, "message": f"Erreur HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "message": str(e)[:120]}


# ============ ASSETS - DELETE ============
@app.delete("/api/assets/{symbol}", tags=["Assets"])
async def delete_asset(symbol: str, db: Session = Depends(get_db)):
    """Supprime un actif et toutes ses positions/transactions."""
    success = AssetCRUD.delete(db, symbol)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{symbol} non trouve")
    return {"success": True, "message": f"{symbol} supprime"}


# ============ PREFERENCES ============
@app.get("/api/settings/preferences", tags=["Settings"])
async def get_preferences(db: Session = Depends(get_db)):
    def _val(key, default):
        s = db.query(AppSetting).filter(AppSetting.key == key).first()
        return s.value if s and s.value else default
    return {
        "investment_horizon": _val("investment_horizon", "long"),
        "risk_appetite":      int(_val("risk_appetite", "3")),
    }

@app.put("/api/settings/preferences", tags=["Settings"])
async def update_preferences(
    investment_horizon: str,
    risk_appetite: int,
    db: Session = Depends(get_db),
):
    if investment_horizon not in ("short", "medium", "long"):
        raise HTTPException(status_code=400, detail="Horizon invalide")
    if not 1 <= risk_appetite <= 5:
        raise HTTPException(status_code=400, detail="Risque entre 1 et 5")
    _save_setting(db, "investment_horizon", investment_horizon)
    _save_setting(db, "risk_appetite", str(risk_appetite))
    return {"success": True}


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
