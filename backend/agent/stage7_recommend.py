"""
Stage 7 — Recommendation

Synthétise Thesis + QuantCheck + RiskAssessment en une Recommendation finale.

Responsabilités :
- Gate final : si QuantCheck.agreement == "contradicts" ET conviction < 60
  → action = "watch" (pas d'achat/vente)
- Détermination de l'action : long → "buy", short → "sell", none → "hold"
- Génération du rationale en français (rationale_fr) et anglais (rationale_en)
  via LLM — court et actionnable (≤ 4 phrases chacun)
- Persistance de la Recommendation avec status="active"
- Mise à jour de SourceWeight.hits/misses lors de la clôture (outcome_pct connu)

Input  : Thesis + QuantCheck + RiskAssessment
Output : Recommendation créée en DB
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from agent.models import Thesis, QuantCheck, RiskAssessment, Recommendation


async def run(
    db: Session,
    thesis: Thesis,
    quant_check: QuantCheck,
    risk: RiskAssessment,
) -> Recommendation:
    """
    Génère la recommandation finale du pipeline.

    Args:
        db:          Session SQLAlchemy active.
        thesis:      Thesis source.
        quant_check: Vérification quantitative.
        risk:        Évaluation de risque.

    Returns:
        Recommendation créée en DB.
    """
    raise NotImplementedError("Stage 7 — à implémenter")


def _determine_action(
    direction: str,
    agreement: str,
    conviction: int,
) -> str:
    """
    Détermine l'action finale (buy | sell | hold | watch).
    Applique les gates de sécurité (agreement contradicts + faible conviction).
    """
    raise NotImplementedError


async def _generate_rationale(
    ticker: str,
    action: str,
    thesis_mechanism: str,
    risk_summary: str,
) -> dict:
    """
    Appel LLM → {rationale_fr: str, rationale_en: str}.
    Prompt court, réponse ≤ 4 phrases par langue.
    """
    raise NotImplementedError


async def close_recommendation(
    db: Session,
    recommendation_id: int,
    outcome_pct: float,
) -> Recommendation:
    """
    Clôture une Recommendation et met à jour SourceWeight (hits/misses).
    outcome_pct > 0 → hit, sinon miss.
    """
    raise NotImplementedError
