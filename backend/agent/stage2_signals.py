"""
Stage 2 — Broad scan & signal detection

Regroupe les articles bruts (RawArticle) en clusters thématiques,
calcule les métriques du cluster et décide si un Signal doit être créé.

Responsabilités :
- Clustering des articles par ticker_primary + event_type + fenêtre temporelle
- Calcul de : volume (nb articles), velocity (articles/heure),
  authority_score (moyenne pondérée des source_tier),
  novelty_score (distance embedding vs articles de la veille — optionnel)
- Création ou mise à jour des Signal en DB
- Promotion vers status="escalated" si les seuils sont dépassés

Seuils (valeurs initiales, à calibrer) :
- weak:   volume >= 2  OR  authority_score >= 0.4
- medium: volume >= 5  AND authority_score >= 0.5
- strong: volume >= 10 OR  authority_score >= 0.8

Input  : articles récents depuis raw_articles (filtrés par fenêtre)
Output : liste d'IDs de Signal créés ou mis à jour
"""
from __future__ import annotations

from typing import List
from sqlalchemy.orm import Session


async def run(db: Session, lookback_hours: int = 24) -> List[int]:
    """
    Scanne les nouveaux articles et détecte les signaux émergents.

    Args:
        db:             Session SQLAlchemy active.
        lookback_hours: Fenêtre temporelle pour les articles à traiter.

    Returns:
        Liste des IDs de Signal créés ou mis à jour.
    """
    raise NotImplementedError("Stage 2 — à implémenter")


def _cluster_articles(articles: list) -> dict:
    """
    Regroupe les articles par (ticker_primary, event_type).
    Retourne un dict {cluster_key: [articles]}.
    """
    raise NotImplementedError


def _compute_authority_score(source_tiers: List[int]) -> float:
    """
    Calcule un score d'autorité 0-1 depuis les tiers de source.
    tier=1 → poids 1.0, tier=5 → poids 0.1 (décroissance linéaire).
    """
    raise NotImplementedError


def _determine_strength(volume: int, authority_score: float) -> str:
    """
    Retourne 'weak' | 'medium' | 'strong' selon les seuils définis.
    """
    raise NotImplementedError
