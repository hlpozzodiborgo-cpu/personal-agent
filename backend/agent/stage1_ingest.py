"""
Stage 1 — Ingest

Collecte des articles bruts depuis toutes les sources configurées.

Responsabilités :
- Interroger chaque source (NewsAPI, RSS, Finnhub news, …)
- Déduplication par URL (upsert dans raw_articles)
- Attribution du source_tier basée sur SourceWeight
- Extraction préliminaire des tickers mentionnés (regex / LLM léger)
- Score de sentiment rapide (heuristique — pas de LLM complet ici)

Input  : liste de symboles du portefeuille (optionnel) + fenêtre temporelle
Output : nombre d'articles nouveaux insérés dans raw_articles
"""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session


async def run(
    db: Session,
    portfolio_symbols: Optional[List[str]] = None,
    lookback_hours: int = 24,
) -> int:
    """
    Lance la collecte de tous les articles récents.

    Args:
        db:                Session SQLAlchemy active.
        portfolio_symbols: Symboles à prioriser (ex: ["ESE.PA", "AAPL"]).
                           Si None, collecte générale sans filtrage.
        lookback_hours:    Fenêtre temporelle en heures.

    Returns:
        Nombre d'articles nouvellement insérés.
    """
    raise NotImplementedError("Stage 1 — à implémenter")


async def _fetch_from_newsapi(
    symbols: List[str],
    api_key: str,
    lookback_hours: int,
) -> List[dict]:
    """Récupère les articles NewsAPI pour les symboles donnés."""
    raise NotImplementedError


async def _fetch_from_finnhub_news(
    symbols: List[str],
    api_key: str,
) -> List[dict]:
    """Récupère les articles Finnhub Company News pour les symboles US."""
    raise NotImplementedError


def _extract_tickers(text: str, known_symbols: List[str]) -> List[str]:
    """
    Extrait les symboles boursiers mentionnés dans un texte.
    Approche rapide : regex sur $TICKER puis match contre known_symbols.
    """
    raise NotImplementedError


def _quick_sentiment(title: str, snippet: str) -> float:
    """
    Score de sentiment rapide [-1, 1] basé sur liste de mots-clés.
    Ne doit pas appeler de LLM — doit être < 1 ms par article.
    """
    raise NotImplementedError
