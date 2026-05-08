"""
Schémas Pydantic pour les actualités et recommandations
Phase 2: News & Recommendations
"""
from pydantic import BaseModel
from typing import Optional, List


class NewsArticle(BaseModel):
    """Schéma pour une actualité"""
    symbol: str
    title: str
    summary: Optional[str] = None
    source: str
    url: str
    published_at: str
    image: Optional[str] = None
    
    class Config:
        from_attributes = True


class Recommendation(BaseModel):
    """Schéma pour une recommandation"""
    symbol: str
    title: str
    summary: Optional[str] = None
    source: str
    url: str
    published_at: str
    sentiment_score: float
    sentiment_label: str
    recommendation_type: str  # BUY, SELL, HOLD, MONITOR
    message: str
    confidence: int  # 0-100
    in_portfolio: bool
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Réponse avec liste de recommandations"""
    recommendations: List[Recommendation]
    count: int
    summary: dict  # {"buy": 2, "sell": 1, "hold": 3}


class EmailNotificationRequest(BaseModel):
    """Requête pour envoyer un email"""
    email: str
    include_all: bool = False  # Si False, envoyer seulement les fortes recommandations
