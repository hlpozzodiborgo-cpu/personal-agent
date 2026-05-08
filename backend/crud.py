"""
Opérations CRUD pour interagir avec la base de données
"""
from sqlalchemy.orm import Session
from datetime import datetime
from models import Asset, Holding, Transaction, PriceHistory, PortfolioSnapshot
import schemas


# ============ ASSETS ============
class AssetCRUD:
    @staticmethod
    def get_or_create(db: Session, symbol: str, name: str, asset_type: str) -> Asset:
        """Récupère ou crée un actif"""
        asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if not asset:
            asset = Asset(symbol=symbol, name=name, asset_type=asset_type)
            db.add(asset)
            db.commit()
            db.refresh(asset)
        return asset
    
    @staticmethod
    def update_price(db: Session, symbol: str, price: float) -> Asset:
        """Met à jour le prix d'un actif"""
        asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if asset:
            asset.current_price = price
            asset.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(asset)
        return asset
    
    @staticmethod
    def get_all(db: Session) -> list:
        """Récupère tous les actifs"""
        return db.query(Asset).all()
    
    @staticmethod
    def get_by_symbol(db: Session, symbol: str) -> Asset:
        """Récupère un actif par son symbole"""
        return db.query(Asset).filter(Asset.symbol == symbol).first()

    @staticmethod
    def delete(db: Session, symbol: str) -> bool:
        """Supprime un actif et toutes ses positions/transactions associées."""
        from models import Holding, Transaction
        asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if not asset:
            return False
        holdings = db.query(Holding).filter(Holding.asset_id == asset.id).all()
        for h in holdings:
            db.query(Transaction).filter(Transaction.holding_id == h.id).delete()
            db.delete(h)
        db.delete(asset)
        db.commit()
        return True


# ============ HOLDINGS ============
class HoldingCRUD:
    @staticmethod
    def create(db: Session, asset_id: int, quantity: float, avg_price: float,
               notes: str = None, purchase_date=None) -> Holding:
        """Crée une nouvelle position"""
        holding = Holding(
            asset_id=asset_id,
            quantity=quantity,
            avg_purchase_price=avg_price,
            total_cost=quantity * avg_price,
            notes=notes,
            purchase_date=purchase_date
        )
        db.add(holding)
        db.commit()
        db.refresh(holding)
        return holding
    
    @staticmethod
    def get_all_active(db: Session) -> list:
        """Récupère toutes les positions actives"""
        return db.query(Holding).filter(Holding.is_active == True).all()
    
    @staticmethod
    def get_by_id(db: Session, holding_id: int) -> Holding:
        """Récupère une position par ID"""
        return db.query(Holding).filter(Holding.id == holding_id).first()
    
    @staticmethod
    def update(db: Session, holding_id: int, quantity: float, avg_price: float) -> Holding:
        """Met à jour une position"""
        holding = db.query(Holding).filter(Holding.id == holding_id).first()
        if holding:
            holding.quantity = quantity
            holding.avg_purchase_price = avg_price
            holding.total_cost = quantity * avg_price
            db.commit()
            db.refresh(holding)
        return holding
    
    @staticmethod
    def delete(db: Session, holding_id: int) -> bool:
        """Marque une position comme inactive"""
        holding = db.query(Holding).filter(Holding.id == holding_id).first()
        if holding:
            holding.is_active = False
            db.commit()
            return True
        return False


# ============ TRANSACTIONS ============
class TransactionCRUD:
    @staticmethod
    def create(db: Session, holding_id: int, transaction_type: str, quantity: float, 
               price_per_unit: float, notes: str = None) -> Transaction:
        """Enregistre une transaction (achat/vente)"""
        transaction = Transaction(
            holding_id=holding_id,
            transaction_type=transaction_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_amount=quantity * price_per_unit,
            notes=notes
        )
        db.add(transaction)
        
        # Met à jour la position
        holding = db.query(Holding).filter(Holding.id == holding_id).first()
        if transaction_type == "buy":
            total_cost = holding.total_cost + (quantity * price_per_unit)
            total_quantity = holding.quantity + quantity
            holding.avg_purchase_price = total_cost / total_quantity if total_quantity > 0 else 0
            holding.quantity = total_quantity
            holding.total_cost = total_cost
        elif transaction_type == "sell":
            holding.quantity = max(0, holding.quantity - quantity)
            if holding.quantity == 0:
                holding.is_active = False
        
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def get_by_holding(db: Session, holding_id: int) -> list:
        """Récupère toutes les transactions d'une position"""
        return db.query(Transaction).filter(Transaction.holding_id == holding_id).order_by(Transaction.date.desc()).all()


# ============ PRICE HISTORY ============
class PriceHistoryCRUD:
    @staticmethod
    def create(db: Session, asset_id: int, price: float) -> PriceHistory:
        """Enregistre un prix historique"""
        ph = PriceHistory(asset_id=asset_id, price=price)
        db.add(ph)
        db.commit()
        db.refresh(ph)
        return ph
    
    @staticmethod
    def get_last_n(db: Session, asset_id: int, n: int = 30) -> list:
        """Récupère les n derniers prix"""
        return db.query(PriceHistory).filter(
            PriceHistory.asset_id == asset_id
        ).order_by(PriceHistory.date.desc()).limit(n).all()
