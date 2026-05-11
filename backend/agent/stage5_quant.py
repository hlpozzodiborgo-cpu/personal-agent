"""
Stage 5 — Quantitative verification

Vérification indépendante de la thèse via données financières objectives.
Ne fait PAS appel au LLM principal — utilise des calculs déterministes
et éventuellement un LLM léger pour l'interprétation des analogues.

Responsabilités :
- Valuation : P/E, P/B, EV/EBITDA vs pairs sectoriels (Yahoo Finance)
- Technique  : tendance (SMA 50/200), momentum (RSI 14), volume
- Facteurs   : value / quality / growth flags simples
- Analogues  : recherche de situations historiques similaires (optionnel)
- Verdict global : confirms | contradicts | neutral

Règle de décision :
  2+ verdicts "bullish" + conviction thèse ≥ 60 → confirms
  2+ verdicts "bearish"                          → contradicts
  sinon                                          → neutral

Input  : Thesis (direction + ticker)
Output : QuantCheck créé en DB
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from agent.models import Thesis, QuantCheck


async def run(db: Session, thesis: Thesis) -> QuantCheck:
    """
    Exécute les vérifications quantitatives pour une thèse.

    Args:
        db:     Session SQLAlchemy active.
        thesis: Thesis à vérifier.

    Returns:
        QuantCheck créé en DB.
    """
    raise NotImplementedError("Stage 5 — à implémenter")


def _valuation_verdict(ticker: str) -> str:
    """
    Calcule le verdict de valorisation depuis Yahoo Finance.
    Retourne 'bullish' | 'bearish' | 'neutral'.
    """
    raise NotImplementedError


def _technical_verdict(ticker: str) -> str:
    """
    Calcule le verdict technique (tendance + momentum).
    Utilise l'API Yahoo Finance historique (même endpoint que finance_service).
    """
    raise NotImplementedError


def _factor_verdict(ticker: str) -> str:
    """
    Vérifie les facteurs value/quality/growth via métriques simples.
    """
    raise NotImplementedError


def _aggregate_verdict(verdicts: list) -> str:
    """
    Agrège les verdicts individuels en verdict global.
    """
    raise NotImplementedError
