"""
Modèles de données pour la gestion des investissements
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Asset(Base):
    """Classe représentant un actif (action, ETF, crypto, etc.)"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)  # AAPL, BTC-USD, etc.
    name = Column(String)  # Apple Inc.
    asset_type = Column(String)  # "stock", "etf", "crypto", "bond"
    current_price = Column(Float, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    holdings = relationship("Holding", back_populates="asset", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="asset", cascade="all, delete-orphan")


class Holding(Base):
    """Classe représentant une position dans le portefeuille"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    quantity = Column(Float)  # Nombre d'actions/pièces
    avg_purchase_price = Column(Float)  # Prix moyen d'achat
    total_cost = Column(Float)  # Investissement total
    date_added = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relations
    asset = relationship("Asset", back_populates="holdings")
    transactions = relationship("Transaction", back_populates="holding", cascade="all, delete-orphan")


class Transaction(Base):
    """Classe pour tracker les achats/ventes"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    holding_id = Column(Integer, ForeignKey("holdings.id"))
    transaction_type = Column(String)  # "buy" ou "sell"
    quantity = Column(Float)
    price_per_unit = Column(Float)
    total_amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relations
    holding = relationship("Holding", back_populates="transactions")


class PriceHistory(Base):
    """Historique des prix pour analyse graphique"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    price = Column(Float)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relations
    asset = relationship("Asset", back_populates="price_history")


class PortfolioSnapshot(Base):
    """Snapshot du portefeuille pour historique"""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    total_value = Column(Float)  # Valeur totale
    total_invested = Column(Float)  # Montant investi
    total_gain_loss = Column(Float)  # Gain/Perte total
    gain_loss_percent = Column(Float)  # % de gain/perte
    date = Column(DateTime, default=datetime.utcnow, index=True)
