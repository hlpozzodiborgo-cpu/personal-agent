"""
Stage 4 — Thesis generation

Génère une thèse d'investissement structurée à partir d'un Signal analysé.

Responsabilités :
- Appel LLM (modèle capable — Claude Sonnet ou Gemini Pro) avec le summary
  du Signal + contexte portefeuille + préférences utilisateur (risk_appetite,
  investment_horizon depuis app_settings)
- Extraction JSON structuré : direction, mechanism, horizon_days,
  magnitude_pct, conviction 0-100, invalidation_conditions
- Filtrage : conviction < 40 → thèse discarded sans créer de QuantCheck
- Persistance du Thesis en DB avec lien signal_id

Input  : Signal (status="escalated", summary rempli)
Output : Thesis créée en DB
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from agent.models import Signal, Thesis


async def run(db: Session, signal: Signal) -> Thesis:
    """
    Génère et persiste une thèse d'investissement.

    Args:
        db:     Session SQLAlchemy active.
        signal: Signal analysé (stage 3 complété).

    Returns:
        Thesis créée, ou Thesis existante si déjà générée pour ce signal.
    """
    raise NotImplementedError("Stage 4 — à implémenter")


async def _generate_thesis_json(
    signal_summary: str,
    portfolio_context: str,
    user_risk_appetite: int,
    user_horizon: str,
) -> dict:
    """
    Appel LLM → dict JSON avec les champs Thesis.
    Le prompt force le format JSON pour parsing fiable.
    """
    raise NotImplementedError


def _validate_thesis_dict(raw: dict) -> dict:
    """
    Valide et sanitise le dict retourné par le LLM.
    Lève ValueError si les champs obligatoires manquent ou sont hors plage.
    """
    raise NotImplementedError
