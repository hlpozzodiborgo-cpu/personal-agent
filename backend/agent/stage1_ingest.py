"""
Stage 1 — Ingest

Collecte des articles bruts depuis GDELT (source unique pour l'instant).

Responsabilités :
- Interroger GDELT Doc 2.0 pour les symboles du portefeuille
- Déduplication par URL canonique puis par hash du titre
- Attribution du source_tier basée sur SOURCE_TIERS
- Extraction préliminaire des tickers mentionnés (regex + alias)
- Score de sentiment rapide via VADER (< 1 ms par article, pas de LLM)

Input  : liste de symboles du portefeuille (optionnel) + fenêtre temporelle
Output : dict {fetched, after_dedupe, persisted}
"""
from __future__ import annotations

import hashlib
import logging
import re
import string
from datetime import datetime
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.orm import Session

from agent.models import RawArticle
from agent.sources.aliases import TICKER_ALIASES, SOURCE_TIERS, alias_to_ticker
from agent.sources.gdelt import fetch_recent_articles

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# VADER — lazy init (import is slow the first time)
# ---------------------------------------------------------------------------

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


# ---------------------------------------------------------------------------
# Stopwords for title deduplication (FR + EN, small hardcoded set)
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "in", "to", "for", "on", "at",
    "is", "are", "was", "were", "be", "been", "has", "have", "had",
    "with", "by", "from", "as", "this", "that", "its", "it",
    "le", "la", "les", "de", "du", "des", "et", "en", "un", "une",
    "au", "aux", "sur", "par", "pour", "que", "qui", "est", "dans",
    "se", "il", "elle", "ils", "elles", "leur", "leurs",
})

# ---------------------------------------------------------------------------
# Event classification keywords
# ---------------------------------------------------------------------------

_EVENT_KEYWORDS: dict[str, list[str]] = {
    "earnings":           ["earnings", "revenue beat", "revenue miss", "eps",
                           "quarterly results", "annual results",
                           "résultats trimestriels", "bénéfice net",
                           "chiffre d'affaires"],
    "merger_acquisition": ["acquires", "acquired by", "merger with",
                           "buyout offer", "takeover bid", "to buy",
                           "fusion avec", "rachat de"],
    "regulatory":         ["sec investigation", "lawsuit", "antitrust",
                           "regulatory fine", "settles", "settlement",
                           "amende", "enquête réglementaire"],
    "macro":              ["fed cuts", "fed raises", "interest rates",
                           "inflation report", "gdp growth", "recession",
                           "central bank", "banque centrale", "bce", "fomc"],
    "analyst_rating":     ["upgrade to", "downgrade to", "price target",
                           "buy rating", "sell rating", "hold rating",
                           "overweight", "underweight", "analyst raises",
                           "analyst lowers"],
    "product":            ["unveils", "announces new", "launches new",
                           "release date", "available today",
                           "dévoile", "lance nouveau"],
}


# ---------------------------------------------------------------------------
# Noise filter
# ---------------------------------------------------------------------------

_NOISE_PATTERNS: list[re.Pattern] = [
    re.compile(r"injured list",           re.I),
    re.compile(r"convicted",              re.I),
    re.compile(r"\bvs\.?\s+\w+",         re.I),   # "Marlins vs. Twins"
    re.compile(r"police|arrested|murder|stolen", re.I),
    re.compile(r"weather|storm|flood|earthquake", re.I),
    re.compile(r"recipe|food|cooking",    re.I),
]


def is_financially_relevant(title: str, tickers: list[str]) -> bool:
    """Retourne False pour les articles sans ticker ou clairement hors finance."""
    if not tickers:
        return False
    text = title.lower()
    return not any(p.search(text) for p in _NOISE_PATTERNS)


# ---------------------------------------------------------------------------
# Public helpers (also used in tests)
# ---------------------------------------------------------------------------

def extract_tickers(text: str, known_symbols: list[str]) -> list[str]:
    """
    Extrait les symboles boursiers mentionnés dans un texte.

    Stratégie :
    1. Regex $TICKER (notation US classique)
    2. Regex mot entier en majuscules contre known_symbols
    3. Alias de TICKER_ALIASES (noms d'entreprises)
    """
    found: set[str] = set()
    known_set = set(known_symbols)

    # Pass 1 — $TICKER notation
    for m in re.finditer(r"\$([A-Z]{1,5})", text):
        sym = m.group(1)
        if sym in known_set:
            found.add(sym)

    # Pass 2 — bare uppercase words / symbols with optional dot-suffix
    for m in re.finditer(r"(?<!\w)([A-Z]{1,5}(?:\.[A-Z]{1,2})?)(?!\w)", text):
        sym = m.group(1)
        if sym in known_set:
            found.add(sym)

    # Pass 3 — company/product name aliases (unigrams + bigrams, plural-tolerant)
    words = text.split()
    for i, word in enumerate(words):
        clean = word.strip(string.punctuation)
        ticker = alias_to_ticker(clean) or alias_to_ticker(clean.rstrip("s"))
        if ticker:
            found.add(ticker)
        # bigrams
        if i < len(words) - 1:
            bigram = clean + " " + words[i + 1].strip(string.punctuation)
            ticker = alias_to_ticker(bigram) or alias_to_ticker(bigram.rstrip("s"))
            if ticker:
                found.add(ticker)

    return sorted(found)


def classify_event(title: str, snippet: str) -> str:
    """
    Classifie un article dans l'une des catégories prédéfinies.
    Approche: keyword matching sur titre + snippet en minuscules.
    """
    text = (title + " " + (snippet or "")).lower()
    for event_type, keywords in _EVENT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return event_type
    return "other"


def score_sentiment(title: str, snippet: str) -> Optional[float]:
    """Score de sentiment VADER dans [-1, 1], ou None si texte non reconnu.

    VADER retourne exactement 0.0 quand aucun mot du lexique n'est trouvé
    (typiquement du texte non-anglais). On retourne None pour distinguer
    ce cas d'un sentiment genuinement neutre.
    """
    text = title + ". " + (snippet or "")
    score = _get_analyzer().polarity_scores(text)["compound"]
    if score == 0.0:
        return None
    return score


def canonicalize_url(url: str) -> str:
    """
    Normalise une URL pour la déduplication :
    - supprime les paramètres utm_* et fbclid
    - supprime le fragment (#…)
    - supprime le www. du host
    - lowercase scheme + host
    - supprime le slash final du path
    """
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        host = parsed.netloc.lower().removeprefix("www.")
        path = parsed.path.rstrip("/")

        # Filter out tracking query params
        _TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign",
                            "utm_term", "utm_content", "fbclid", "gclid",
                            "ref", "source"}
        qs = parse_qs(parsed.query, keep_blank_values=False)
        filtered = {k: v for k, v in qs.items() if k.lower() not in _TRACKING_PARAMS}
        new_query = urlencode(filtered, doseq=True)

        return urlunparse((scheme, host, path, "", new_query, ""))
    except Exception:
        return url.lower().rstrip("/")


def dedupe_articles(articles: list[dict]) -> list[dict]:
    """
    Déduplication en deux passes :
    1. Par URL canonique (garde le premier vu)
    2. Par hash MD5 du titre normalisé (sans stopwords)
    """
    seen_urls: set[str] = set()
    seen_title_hashes: set[str] = set()
    result: list[dict] = []

    for art in articles:
        # Pass 1 — URL
        canon = canonicalize_url(art.get("url", ""))
        if canon in seen_urls:
            continue
        seen_urls.add(canon)

        # Pass 2 — title hash
        title = art.get("title", "").lower()
        title = title.translate(str.maketrans("", "", string.punctuation))
        tokens = [w for w in title.split() if w not in _STOPWORDS]
        title_hash = hashlib.md5(" ".join(tokens).encode()).hexdigest()
        if title_hash in seen_title_hashes:
            continue
        seen_title_hashes.add(title_hash)

        result.append(art)

    return result


def persist_articles(db: Session, articles: list[dict], known_symbols: list[str]) -> int:
    count = 0
    noise_skipped = 0
    now = datetime.utcnow()

    for art in articles:
        url = art["url"]
        # Skip si déjà en DB
        if db.query(RawArticle).filter(RawArticle.url == url).first():
            continue

        domain = art.get("source", "")
        tier = SOURCE_TIERS.get(domain, SOURCE_TIERS["default"])
        tickers = extract_tickers(art.get("title", ""), known_symbols)

        if not is_financially_relevant(art.get("title", ""), tickers):
            noise_skipped += 1
            continue

        event_type = classify_event(art.get("title", ""), "")
        sentiment = score_sentiment(art.get("title", ""), "")

        pub_str = art.get("published_at", "")
        try:
            published_at = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
        except Exception:
            published_at = None

        row = RawArticle(
            source=domain, source_tier=tier, url=url,
            title=art["title"], content=None,
            published_at=published_at, fetched_at=now,
            tickers=tickers or None, event_type=event_type,
            raw_sentiment=sentiment,
        )
        db.add(row)
        try:
            db.commit()
            count += 1
        except Exception as exc:
            logger.warning("persist_articles: skip URL %s — %s", url, exc)
            db.rollback()

    if noise_skipped:
        logger.info("persist_articles: skipped %d non-financial articles", noise_skipped)
    return count


# Tickers utilisés quand aucun portefeuille n'est fourni — 5 max pour
# rester dans les limites de la query GDELT.
TOP_DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "MC.PA"]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def run(
    db: Session,
    portfolio_symbols: Optional[list[str]] = None,
    lookback_hours: int = 24,
) -> dict:
    """
    Lance la collecte d'articles GDELT et retourne les compteurs.

    Returns:
        {"fetched": int, "after_dedupe": int, "persisted": int}
    """
    tickers = portfolio_symbols or TOP_DEFAULT_TICKERS

    # Construire les termes de recherche à partir des alias (noms d'entreprise)
    # plutôt que des symboles bruts qui n'apparaissent pas dans les articles.
    search_terms: list[str] = []
    for ticker in tickers:
        aliases = TICKER_ALIASES.get(ticker, [])
        search_terms.extend(aliases[:2])
    search_terms = [t for t in search_terms if len(t) >= 4]
    if not search_terms:
        search_terms = tickers  # fallback si aucun alias connu

    logger.info("Stage 1: search_terms = %s", search_terms)

    raw = await fetch_recent_articles(search_terms, hours_back=lookback_hours)
    deduped = dedupe_articles(raw)
    persisted = persist_articles(db, deduped, tickers)

    result = {
        "fetched":      len(raw),
        "after_dedupe": len(deduped),
        "persisted":    persisted,
    }
    logger.info("Stage 1 ingest complete: %s", result)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio
    import sys

    from agent.deps import get_db

    symbols = sys.argv[1:] or []
    db = next(get_db())
    try:
        result = asyncio.run(run(db, portfolio_symbols=symbols or None, lookback_hours=24))
        print(result)
    finally:
        db.close()
