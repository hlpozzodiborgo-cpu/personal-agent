"""
Routes pour les actualités et recommandations
Phase 2: News & Recommendations endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from config import FINNHUB_API_KEY
from news_service import NewsService
from recommendation_engine import RecommendationEngine
from schemas_news import Recommendation, RecommendationResponse, EmailNotificationRequest
from email_service import EmailService

logger = logging.getLogger(__name__)

# Créer le routeur
router = APIRouter(prefix="/api/news", tags=["News & Recommendations"])


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    symbols: str = None,  # Symboles séparés par virgules (ex: "AAPL,MSFT")
    hours: int = 24,  # Considérer les actualités des dernières X heures
) -> RecommendationResponse:
    """
    Récupère les recommandations basées sur les actualités récentes
    
    Query parameters:
    - symbols: Symboles à analyser (ex: "AAPL,MSFT,GOOGL")
    - hours: Nombre d'heures à considérer (défaut: 24)
    
    Returns:
    - Recommandations classées par pertinence
    """
    
    if not symbols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paramètre 'symbols' requis (ex: ?symbols=AAPL,MSFT)"
        )
    
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    logger.info(f"📰 Analyse des recommandations pour: {symbol_list}")
    
    try:
        # Récupérer les actualités
        all_news = NewsService.get_news_for_portfolio(symbol_list, FINNHUB_API_KEY)
        
        # Filtrer les actualités récentes
        recent_news = NewsService.filter_recent_news(all_news, hours=hours)
        
        logger.info(f"📰 {len(recent_news)} actualités récentes trouvées")
        
        # Générer les recommandations
        recommendations = [
            RecommendationEngine.generate_recommendation(
                NewsService.get_article_details(article),
                symbol_list
            )
            for article in recent_news
        ]
        
        # Classer par pertinence
        ranked = RecommendationEngine.rank_recommendations(recommendations)
        
        # Calculer le résumé
        summary = {
            "buy": sum(1 for r in ranked if "BUY" in r['recommendation_type']),
            "sell": sum(1 for r in ranked if "SELL" in r['recommendation_type']),
            "hold": sum(1 for r in ranked if "HOLD" in r['recommendation_type']),
            "monitor": sum(1 for r in ranked if "MONITOR" in r['recommendation_type']),
        }
        
        logger.info(f"✅ {len(ranked)} recommandations générées")
        
        return RecommendationResponse(
            recommendations=ranked,
            count=len(ranked),
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération des recommandations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/recommendations/portfolio")
async def get_portfolio_recommendations(
    # Les symboles seront passés du frontend comme les ETFs du portefeuille
    symbols: str = None,
    hours: int = 24
):
    """
    Récupère les recommandations pour tout le portefeuille
    (Endpoint simplifié qui utilise get_recommendations)
    """
    return await get_recommendations(symbols=symbols, hours=hours)


@router.post("/send-recommendations")
async def send_recommendations_email(request: EmailNotificationRequest) -> dict:
    """
    Envoie les recommandations par email
    
    Body:
    {
        "email": "user@example.com",
        "include_all": false  # Si false, seulement les fortes recommandations
    }
    """
    
    if not request.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email requis"
        )
    
    try:
        logger.info(f"📧 Envoi des recommandations à {request.email}")
        
        # Récupérer les symboles du portefeuille
        # NOTE: À adapter selon comment tu récupères les symboles du portefeuille
        symbol_list = ["AAPL", "MSFT", "GOOGL"]  # TODO: à remplacer
        
        # Récupérer les actualités et générer les recommandations
        all_news = NewsService.get_news_for_portfolio(symbol_list, FINNHUB_API_KEY)
        recommendations = [
            RecommendationEngine.generate_recommendation(
                NewsService.get_article_details(article),
                symbol_list
            )
            for article in all_news
        ]
        
        # Filtrer si needed
        if not request.include_all:
            recommendations = [r for r in recommendations if r['confidence'] >= 60]
        
        ranked = RecommendationEngine.rank_recommendations(recommendations)
        
        # Envoyer l'email
        success = EmailService.send_recommendation_email(request.email, ranked)
        
        if success:
            return {
                "status": "success",
                "message": f"Email envoyé à {request.email}",
                "recommendations_count": len(ranked)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Impossible d'envoyer l'email"
            )
    
    except Exception as e:
        logger.error(f"❌ Erreur envoi email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/test-email")
async def test_email(email: str) -> dict:
    """
    Envoie un email de test
    
    Query parameter:
    - email: adresse email pour le test
    """
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email requis"
        )
    
    success = EmailService.test_email_config(email)
    
    if success:
        return {"status": "success", "message": f"Email de test envoyé à {email}"}
    else:
        return {"status": "error", "message": "Impossible d'envoyer l'email de test"}


@router.get("/debug/symbols")
async def debug_symbols_news(symbols: str = None):
    """
    Endpoint de debugging - teste les actualités pour chaque symbole individuellement
    
    Query parameter:
    - symbols: Symboles séparés par virgules
    """
    if not symbols:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paramètre 'symbols' requis"
        )
    
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    debug_results = {}
    
    for symbol in symbol_list:
        try:
            news = NewsService.get_news_for_symbol(symbol, FINNHUB_API_KEY)
            debug_results[symbol] = {
                "status": "ok",
                "articles_count": len(news),
                "sample": news[0] if news else None
            }
        except Exception as e:
            debug_results[symbol] = {
                "status": "error",
                "error": str(e)
            }
    
    return {
        "symbols_tested": symbol_list,
        "results": debug_results,
        "total_articles": sum(v.get("articles_count", 0) for v in debug_results.values() if v.get("status") == "ok")
    }
