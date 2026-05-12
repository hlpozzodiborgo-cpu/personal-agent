"""
Yahoo Finance News source adapter.

Récupère les actualités taggées par ticker via yfinance — aucune clé API,
sources premium (Reuters, Bloomberg, CNBC, MarketWatch), couverture ETF/ADR.

Différence clé vs GDELT : fetch() reçoit des SYMBOLES BRUTS (AAPL, MSFT),
pas des search_terms (Apple, iPhone). Yahoo tagge ses articles par ticker.

Compatibilité : gère à la fois l'ancien format yfinance (< 0.2.50, clés
providerPublishTime/link/title) et le nouveau format imbriqué (>= 0.2.50,
clé content avec pubDate/canonicalUrl/title).
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import yfinance as yf

from agent.sources.base import NewsSource

logger = logging.getLogger(__name__)


def _parse_article(art: dict, cutoff: float) -> dict[str, Any] | None:
    """Parse new (content-nested) or legacy (flat) yfinance article format.

    Returns None if the article is outside the time window or has missing fields.
    """
    content = art.get("content")
    if content:
        # Nouveau format (yfinance >= ~0.2.50)
        title   = content.get("title", "").strip()
        url     = ((content.get("canonicalUrl") or {}).get("url", "") or
                   (content.get("clickThroughUrl") or {}).get("url", "")).strip()
        pub_str = content.get("pubDate", "")
        try:
            pub_ts = datetime.fromisoformat(pub_str.replace("Z", "+00:00")).timestamp()
        except Exception:
            pub_ts = 0.0
        # Domaine depuis l'URL, fallback sur sourceId du provider
        if url:
            domain = urlparse(url).netloc.lower().removeprefix("www.")
        else:
            domain = (content.get("provider") or {}).get("sourceId", "")
    else:
        # Ancien format (providerPublishTime + link au niveau racine)
        title  = art.get("title", "").strip()
        url    = art.get("link", "").strip()
        pub_ts = float(art.get("providerPublishTime", 0))
        domain = urlparse(url).netloc.lower().removeprefix("www.") if url else ""

    if not title or not url or pub_ts < cutoff:
        return None

    return {
        "source":       domain,
        "url":          url,
        "title":        title,
        "published_at": datetime.fromtimestamp(pub_ts, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "content":      None,
        "language":     "english",
    }


class YFinanceSource(NewsSource):
    """Yahoo Finance News par ticker. Aucune clé API requise."""

    name = "yfinance"
    default_tier = 2

    async def fetch(
        self,
        tickers: list[str],
        hours_back: int = 24,
    ) -> list[dict[str, Any]]:
        """
        Récupère les actualités Yahoo Finance pour chaque ticker.

        Reçoit des symboles bruts (AAPL, MSFT) — pas des search_terms.
        Filtre les articles plus anciens que hours_back heures.
        Gère les erreurs par ticker sans bloquer les autres.
        """
        cutoff  = datetime.now(timezone.utc).timestamp() - hours_back * 3600
        results: list[dict[str, Any]] = []

        for symbol in tickers:
            try:
                def _get_news(sym: str = symbol) -> list[dict]:
                    return yf.Ticker(sym).news or []

                news  = await asyncio.to_thread(_get_news)
                count = 0
                for art in news:
                    parsed = _parse_article(art, cutoff)
                    if parsed:
                        results.append(parsed)
                        count += 1
                logger.info("yfinance %s: %d articles in window", symbol, count)
            except Exception as exc:
                logger.warning("yfinance %s failed: %s", symbol, exc)

            await asyncio.sleep(0.2)

        return results
