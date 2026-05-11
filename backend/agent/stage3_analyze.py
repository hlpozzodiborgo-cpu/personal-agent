"""
Stage 3 — Deep read & analysis

Pour chaque Signal escaladed, effectue une lecture approfondie par LLM
du contenu complet des articles associés.

Responsabilités :
- Récupérer les articles liés au Signal (joints via tickers + fenêtre)
- Appel LLM avec le contenu complet (pas seulement titre + snippet)
- Extraction structurée : event_type, chiffres clés, ton du management,
  catalyseurs identifiés, risques mentionnés
- Cross-reference avec les positions du portefeuille utilisateur
  (pour contextualiser la pertinence)
- Enrichissement du RawArticle.event_type et mise à jour du Signal.summary

Input  : Signal avec status="escalated"
Output : Signal.summary mis à jour, articles enrichis
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from agent.models import Signal


async def run(db: Session, signal: Signal) -> Signal:
    """
    Analyse approfondie d'un Signal via LLM.

    Args:
        db:     Session SQLAlchemy active.
        signal: Signal escalated à analyser.

    Returns:
        Signal mis à jour avec summary enrichi.
    """
    raise NotImplementedError("Stage 3 — à implémenter")


async def _deep_read_articles(
    articles: list,
    signal: Signal,
    portfolio_context: str,
) -> str:
    """
    Appel LLM pour lecture approfondie.
    Retourne un résumé structuré (summary) à stocker sur le Signal.
    """
    raise NotImplementedError


def _build_portfolio_context(portfolio_holdings: list) -> str:
    """
    Construit le contexte texte du portefeuille à injecter dans le prompt.
    Format : "ESE.PA (S&P 500 ETF): 24 parts, PRU 27.50€, +15.2%"
    """
    raise NotImplementedError
