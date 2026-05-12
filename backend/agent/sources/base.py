"""
Interface commune pour toutes les sources de news de l'agent pipeline.

Chaque source implémente NewsSource et retourne des dicts au format unifié.
Ajouter une nouvelle source = créer une classe de ~80 lignes dans sources/.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class NewsSource(ABC):
    """Interface commune pour toutes les sources de news.

    Une source retourne une liste de dicts au format unifié :
      {
          "source":       str,         # domaine (ex: "reuters.com")
          "url":          str,         # URL canonique de l'article
          "title":        str,         # titre brut
          "published_at": str,         # ISO-8601 (ex: "2026-05-11T14:30:00Z")
          "content":      str | None,  # snippet ou None
          "language":     str | None,  # "english" / "french" / etc.
      }
    """

    name: str         # ex: "gdelt", "yfinance"
    default_tier: int  # 1 (premium) → 5 (low-quality)

    @abstractmethod
    async def fetch(
        self,
        tickers: list[str],
        hours_back: int = 24,
    ) -> list[dict[str, Any]]:
        """Récupère les articles récents pour les termes de recherche donnés.

        Args:
            tickers:    Termes de recherche (noms d'entreprise ou symboles
                        selon la source). Construits par stage1_ingest.run().
            hours_back: Fenêtre temporelle en heures.

        Returns:
            Liste de dicts au format unifié. Jamais de raise — retourne []
            en cas d'erreur réseau ou API.
        """
        ...
