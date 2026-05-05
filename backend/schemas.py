"""
Schemas Pydantic pour validation des données API
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


# ============ ASSET ============
class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: str  # "stock", "etf", "crypto", "bond"

class AssetCreate(AssetBase):
    pass

class Asset(AssetBase):
    id: int
    current_price: float
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ============ HOLDING ============
class TransactionSchema(BaseModel):
    transaction_type: str  # "buy" ou "sell"
    quantity: float
    price_per_unit: float
    date: Optional[datetime] = None
    notes: Optional[str] = None


class HoldingBase(BaseModel):
    quantity: float
    avg_purchase_price: float
    notes: Optional[str] = None

class HoldingCreate(HoldingBase):
    asset_id: int

class Holding(HoldingBase):
    id: int
    asset_id: int
    total_cost: float
    date_added: datetime
    is_active: bool
    asset: Asset
    
    class Config:
        from_attributes = True


# ============ PORTFOLIO STATS ============
class PortfolioStats(BaseModel):
    total_invested: float = Field(description="Montant total investi")
    total_current_value: float = Field(description="Valeur actuelle du portefeuille")
    total_gain_loss: float = Field(description="Gain/Perte total en €")
    gain_loss_percent: float = Field(description="% de gain/perte")
    number_of_holdings: int = Field(description="Nombre de positions")
    last_updated: datetime


class PortfolioDetailResponse(BaseModel):
    stats: PortfolioStats
    holdings: List[dict]  # Liste des positions avec détails
    top_gainer: Optional[dict] = None
    top_loser: Optional[dict] = None


# ============ TRANSACTION ============
class TransactionCreate(BaseModel):
    holding_id: int
    transaction_type: str
    quantity: float
    price_per_unit: float
    notes: Optional[str] = None

class Transaction(TransactionCreate):
    id: int
    date: datetime
    total_amount: float
    
    class Config:
        from_attributes = True
