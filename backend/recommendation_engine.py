"""
Moteur de recommandations basé sur les actualités et le sentiment
Phase 2: Analyse simple du sentiment des actualités
"""
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyse simple du sentiment d'un texte"""
    
    # Mots positifs pour les investissements
    POSITIVE_KEYWORDS = {
        'growth', 'rise', 'gain', 'profit', 'up', 'strong', 'beat', 'surge',
        'rally', 'recover', 'bounce', 'rebound', 'jump', 'soar', 'boom',
        'revenue', 'earnings', 'record', 'expansion', 'partnership', 'deal',
        'acquisition', 'innovation', 'breakthrough', 'award', 'leadership',
        'outperform', 'bullish', 'positive', 'upgrade', 'buyback',
        'divident', 'dividend', 'analyst', 'target', 'price', 'écouteurs',
        'launch', 'product', 'success', 'momentum', 'rally', 'rebound'
    }
    
    # Mots négatifs
    NEGATIVE_KEYWORDS = {
        'loss', 'fall', 'down', 'decline', 'drop', 'crash', 'weak', 'miss',
        'plunge', 'sink', 'slump', 'tumble', 'bankruptcy', 'lawsuit',
        'scandal', 'investigation', 'fine', 'penalty', 'recall', 'risk',
        'warning', 'downgrade', 'bearish', 'negative', 'concerns', 'fears',
        'threat', 'inflation', 'recession', 'layoffs', 'restructuring',
        'controversy', 'fraud', 'failure', 'break', 'problem', 'issue',
        'deficit', 'loss'
    }
    
    @staticmethod
    def analyze_text(text: str) -> float:
        """
        Analyse le sentiment d'un texte
        
        Args:
            text: Texte à analyser (titre ou résumé)
            
        Returns:
            Score de sentiment entre -1 (très négatif) et +1 (très positif)
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Compter les mots positifs et négatifs
        positive_count = sum(1 for word in SentimentAnalyzer.POSITIVE_KEYWORDS 
                           if word in text_lower)
        negative_count = sum(1 for word in SentimentAnalyzer.NEGATIVE_KEYWORDS 
                           if word in text_lower)
        
        # Calculer le score
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        score = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, score))  # Limiter entre -1 et 1

    @staticmethod
    def get_sentiment_label(score: float) -> str:
        """Retourne un label texte pour le score"""
        if score > 0.3:
            return "Positif 📈"
        elif score < -0.3:
            return "Négatif 📉"
        else:
            return "Neutre"


class RecommendationEngine:
    """Moteur de recommandations basé sur les actualités"""
    
    @staticmethod
    def generate_recommendation(article: Dict, portfolio_symbols: List[str]) -> Dict:
        """
        Génère une recommandation basée sur une actualité
        
        Args:
            article: Données de l'article avec 'title', 'summary', 'symbol'
            portfolio_symbols: Symboles du portefeuille de l'utilisateur
            
        Returns:
            Dictionnaire avec la recommandation
        """
        symbol = article.get('symbol', '')
        title = article.get('title', '')
        summary = article.get('summary', '')
        published_at = article.get('published_at', '')
        
        # Analyser le sentiment
        title_sentiment = SentimentAnalyzer.analyze_text(title)
        summary_sentiment = SentimentAnalyzer.analyze_text(summary)
        
        # Moyenne pondérée (titre compte plus)
        overall_sentiment = (title_sentiment * 0.6 + summary_sentiment * 0.4)
        sentiment_label = SentimentAnalyzer.get_sentiment_label(overall_sentiment)
        
        # Déterminer le type de recommandation
        recommendation_type = RecommendationEngine._get_recommendation_type(
            symbol, overall_sentiment, title, portfolio_symbols
        )
        
        # Générer le message
        message = RecommendationEngine._generate_message(
            symbol, sentiment_label, recommendation_type, title
        )
        
        # Calculer la confiance (0 à 100)
        confidence = int(abs(overall_sentiment) * 100)
        
        return {
            'symbol': symbol,
            'title': title,
            'summary': summary,
            'source': article.get('source', 'Unknown'),
            'url': article.get('url', ''),
            'published_at': published_at,
            'sentiment_score': round(overall_sentiment, 2),
            'sentiment_label': sentiment_label,
            'recommendation_type': recommendation_type,  # 'BUY', 'SELL', 'HOLD', 'MONITOR'
            'message': message,
            'confidence': confidence,
            'in_portfolio': symbol in portfolio_symbols
        }

    @staticmethod
    def _get_recommendation_type(symbol: str, sentiment: float, 
                                title: str, portfolio_symbols: List[str]) -> str:
        """Détermine le type de recommandation"""
        in_portfolio = symbol in portfolio_symbols
        
        if sentiment > 0.4:
            return "BUY 🟢"
        elif sentiment < -0.4:
            return "SELL 🔴" if in_portfolio else "MONITOR 🟡"
        else:
            return "HOLD ⚪"

    @staticmethod
    def _generate_message(symbol: str, sentiment: str, 
                         rec_type: str, title: str) -> str:
        """Génère un message de recommandation lisible"""
        emoji_map = {
            "BUY 🟢": "📈",
            "SELL 🔴": "📉",
            "HOLD ⚪": "↔️",
            "MONITOR 🟡": "👀"
        }
        emoji = emoji_map.get(rec_type, "")
        
        return f"{emoji} {rec_type.split()[0]}: {symbol} ({sentiment})"

    @staticmethod
    def rank_recommendations(recommendations: List[Dict]) -> List[Dict]:
        """
        Classe les recommandations par pertinence
        
        Args:
            recommendations: Liste des recommandations
            
        Returns:
            Liste triée par confiance et pertinence
        """
        def score_recommendation(rec: Dict) -> tuple:
            # Priorité: recommandations du portefeuille, puis par confiance
            in_portfolio = 0 if rec['in_portfolio'] else 1
            confidence = -rec['confidence']  # Négatif pour reverse sort
            return (in_portfolio, confidence)
        
        return sorted(recommendations, key=score_recommendation)
