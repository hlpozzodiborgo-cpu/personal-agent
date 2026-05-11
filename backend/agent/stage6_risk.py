"""
Stage 6 — Risk assessment

Évalue le risque de la thèse dans le contexte du portefeuille actuel.

Responsabilités :
- Drawdown attendu : basé sur la volatilité historique du ticker (Yahoo Finance)
  et le magnitude_pct de la thèse (scénario adverse)
- Beta : régression 90J rendements ticker vs indice de référence (^GSPC ou ^STOXX50E)
- Corrélation au portefeuille : éviter la concentration sur un même facteur
- Liquidité : volume moyen journalier > seuil pour position suggérée
- Taille suggérée : 1/2 Kelly simplifié, plafonné par risk_appetite utilisateur
- Scénarios : bull / base / bear avec rendement et probabilité estimés

Seuil de liquidité : volume_moyen_jour × prix > 10 × taille_position_€

Input  : Thesis + QuantCheck (agreement) + holdings actifs
Output : RiskAssessment créé en DB
"""
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session
from agent.models import Thesis, QuantCheck, RiskAssessment


async def run(
    db: Session,
    thesis: Thesis,
    quant_check: QuantCheck,
    portfolio_holdings: List[dict],
    user_risk_appetite: int,
) -> RiskAssessment:
    """
    Calcule l'évaluation de risque pour une thèse vérifiée.

    Args:
        db:                  Session SQLAlchemy active.
        thesis:              Thesis source.
        quant_check:         QuantCheck associé (pour l'agreement).
        portfolio_holdings:  Positions actives [{symbol, quantity, …}].
        user_risk_appetite:  1-5 depuis app_settings.

    Returns:
        RiskAssessment créé en DB.
    """
    raise NotImplementedError("Stage 6 — à implémenter")


def _estimate_drawdown(ticker: str, magnitude_pct: float) -> float:
    """
    Estime le drawdown attendu dans le scénario adverse.
    Utilise la volatilité historique 90J (σ) : drawdown = 2σ + |magnitude_pct|.
    """
    raise NotImplementedError


def _compute_beta(ticker: str, benchmark: str = "^GSPC") -> float:
    """
    Calcule le beta sur 90 jours de données journalières.
    """
    raise NotImplementedError


def _portfolio_correlation(ticker: str, holdings: List[dict]) -> float:
    """
    Corrélation entre le ticker et le portefeuille pondéré (valeur).
    """
    raise NotImplementedError


def _kelly_size(conviction: int, win_rate: float, risk_appetite: int) -> float:
    """
    Taille de position via fraction de Kelly simplifiée.
    Plafonnée à risk_appetite × 4 % (ex: risque 3 → max 12 %).
    """
    raise NotImplementedError


def _build_scenarios(
    ticker: str,
    direction: str,
    magnitude_pct: float,
    horizon_days: int,
) -> dict:
    """
    Construit les scénarios {bull, base, bear} avec rendement et probabilité.
    """
    raise NotImplementedError
