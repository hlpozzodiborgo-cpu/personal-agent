"""
Pipeline orchestrateur — enchaîne les 7 stages.

Responsabilités :
- Lire les symboles du portefeuille actif depuis la DB Phase 1
- Lire les préférences utilisateur (risk_appetite, investment_horizon)
- Appeler les stages dans l'ordre : 1 → 2 → 3 → 4 → 5 → 6 → 7
- Gérer les erreurs stage par stage (un stage raté ne bloque pas les suivants)
- Retourner un résumé d'exécution (PipelineRunResponse)

Usage :
    from agent.pipeline import run_pipeline
    result = await run_pipeline(db)
"""
from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from agent import schemas as agent_schemas

logger = logging.getLogger(__name__)


async def run_pipeline(db: Session) -> agent_schemas.PipelineRunResponse:
    """
    Lance le pipeline complet de la collecte à la recommandation.

    Args:
        db: Session SQLAlchemy active (partagée avec main.py via get_db).

    Returns:
        PipelineRunResponse avec le compte-rendu d'exécution.
    """
    raise NotImplementedError("Pipeline — à implémenter")
