"""
GDELT Doc 2.0 source adapter.

Fetches recent articles via the GDELT ArtList API — free, no key required,
global coverage, ~15 min refresh cadence.

API reference: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""
from __future__ import annotations

import asyncio
import logging
import re
import time
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

_GDELT_BASE = "https://api.gdeltproject.org/api/v2/doc/doc"
_USER_AGENT = "InvestorAI/1.0 (research bot; contact: hlpozzodiborgo@gmail.com)"

_RATE_LIMIT_SECONDS = 5.0
_last_request_at: float = 0.0


async def _enforce_rate_limit() -> None:
    """GDELT documente 1 req/5s. Bloque jusqu'à ce que ce soit safe."""
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < _RATE_LIMIT_SECONDS:
        await asyncio.sleep(_RATE_LIMIT_SECONDS - elapsed)
    _last_request_at = time.monotonic()


def _build_url(query: str, hours_back: int, max_records: int) -> str:
    params = {
        "query":      query,
        "mode":       "ArtList",
        "format":     "json",
        "timespan":   f"{hours_back}H",
        "sourcelang": "english",
        "maxrecords": str(max_records),
    }
    return f"{_GDELT_BASE}?{urlencode(params)}"


def _parse_seendate(seendate: str) -> str:
    """Convert GDELT seendate (YYYYMMDDTHHmmssZ) to ISO-8601."""
    try:
        # e.g. "20240315T143022Z" → "2024-03-15T14:30:22Z"
        s = seendate.replace("T", "").replace("Z", "")
        return (
            f"{s[0:4]}-{s[4:6]}-{s[6:8]}T"
            f"{s[8:10]}:{s[10:12]}:{s[12:14]}Z"
        )
    except Exception:
        return seendate


async def fetch_recent_articles(
    search_terms: list[str],
    hours_back: int = 24,
    max_records: int = 250,
) -> list[dict]:
    """
    Fetch recent articles from GDELT matching any of the given search terms.

    search_terms doit contenir des noms d'entreprise (ex: "Apple", "Nvidia"),
    pas des symboles boursiers bruts ("AAPL"). La construction des termes
    à partir des tickers est la responsabilité de l'appelant.

    Returns a list of normalized dicts:
        {url, title, published_at, source (domain), language}

    Always returns [] on network or HTTP errors — never raises.
    """
    if not search_terms:
        return []

    # GDELT exige que les termes OR soient entourés de parenthèses
    query = "(" + " OR ".join(f'"{t}"' for t in search_terms) + ")"
    url = _build_url(query, hours_back, max_records)

    await _enforce_rate_limit()

    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)

        if resp.status_code != 200:
            logger.warning("GDELT returned HTTP %d for query %r", resp.status_code, query)
            return []

        data = resp.json()
        raw_articles = data.get("articles") or []

        _LATIN_RE = re.compile(r'^[\x00-\xffĀ-ſ]*$')
        _ALLOWED_LANGS = {"english", "french"}

        results: list[dict] = []
        lang_skipped = 0
        for art in raw_articles:
            article_url = art.get("url", "").strip()
            title = art.get("title", "").strip()
            if not article_url or not title:
                continue
            # Filtre langue : conserver uniquement l'anglais et le français
            lang = art.get("language", "").lower()
            if lang not in _ALLOWED_LANGS:
                lang_skipped += 1
                continue
            # Filtre charset : rejeter les titres hors ASCII/Latin (CJK, arabe, coréen…)
            if not _LATIN_RE.match(title):
                lang_skipped += 1
                continue
            results.append({
                "url":          article_url,
                "title":        title,
                "published_at": _parse_seendate(art.get("seendate", "")),
                "source":       art.get("domain", ""),
                "language":     lang,
            })

        if lang_skipped:
            logger.info("GDELT: skipped %d articles (non-EN/FR or non-Latin charset)", lang_skipped)
        logger.info("GDELT: fetched %d articles for terms %s", len(results), search_terms)
        return results

    except httpx.TimeoutException:
        logger.warning("GDELT request timed out — query too large? terms=%s", search_terms)
        return []
    except Exception as exc:
        logger.warning("GDELT fetch failed: %s", exc)
        return []
