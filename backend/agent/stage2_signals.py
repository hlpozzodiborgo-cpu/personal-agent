"""
Stage 2 — Signal detection

Clusterise les articles bruts (Stage 1) par ticker + similarité sémantique,
score chaque cluster, et génère des Signals pour les clusters non-faibles.

Pipeline :
  1. Récupérer les articles non-traités dans la fenêtre temporelle
  2. Embedder les titres (sentence-transformers, all-MiniLM-L6-v2)
  3. Clusteriser par ticker primaire + similarité cosine
  4. Scorer chaque cluster (volume, vélocité, autorité, nouveauté)
  5. Classifier weak / medium / strong
  6. Persister les Signals status=pending
  7. Marquer les articles processed_at = NOW
"""
from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy.orm import Session

from agent.models import RawArticle, Signal

logger = logging.getLogger(__name__)

_SIMILARITY_THRESHOLD = 0.70
_MIN_CLUSTER_SIZE     = 2
_MODEL_NAME           = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model (~30s first time)")
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_titles(titles: list[str]) -> np.ndarray:
    """Retourne une matrice (N, 384) d'embeddings normalisés L2."""
    model = _get_model()
    return model.encode(titles, normalize_embeddings=True, show_progress_bar=False)


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------

def cluster_articles_by_ticker(
    articles: list[RawArticle],
    embeddings: np.ndarray,
    threshold: float = _SIMILARITY_THRESHOLD,
) -> dict[int, list[int]]:
    """
    Cluster articles WITHIN each primary ticker group.

    Retourne {global_cluster_label: [article_indices]}.
    Label -1 = articles sans ticker ou groupe de 1 article.
    Labels >= 0 = clusters candidats filtrés par _MIN_CLUSTER_SIZE dans run().
    """
    clusters: dict[int, list[int]] = {}
    global_offset = 0

    ticker_groups: dict[str, list[int]] = {}
    for i, art in enumerate(articles):
        if art.tickers and len(art.tickers) > 0:
            primary = art.tickers[0]
            ticker_groups.setdefault(primary, []).append(i)
        else:
            clusters.setdefault(-1, []).append(i)

    distance_threshold = 1.0 - threshold

    for ticker, indices in ticker_groups.items():
        if len(indices) < 2:
            clusters.setdefault(-1, []).extend(indices)
            continue

        group_embs = embeddings[np.array(indices)]
        try:
            agg = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=distance_threshold,
                metric="cosine",
                linkage="average",
            )
            labels = agg.fit_predict(group_embs)
        except Exception as exc:
            logger.warning(
                "Clustering failed for ticker %s: %s — fallback label -1", ticker, exc
            )
            clusters.setdefault(-1, []).extend(indices)
            continue

        n_labels = int(labels.max()) + 1
        for local_i, global_idx in enumerate(indices):
            global_label = global_offset + int(labels[local_i])
            clusters.setdefault(global_label, []).append(global_idx)
        global_offset += n_labels

    return clusters


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

_TIER_WEIGHTS = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4, 5: 0.2}


def compute_authority(articles: list[RawArticle]) -> float:
    """Moyenne des poids inversés de source_tier. Float dans [0.2, 1.0]."""
    weights = [_TIER_WEIGHTS.get(a.source_tier, 0.6) for a in articles]
    return sum(weights) / len(weights) if weights else 0.6


def compute_velocity(articles: list[RawArticle]) -> float:
    """Articles par heure entre le premier et le dernier published_at. Max 20.0."""
    times = [a.published_at for a in articles if a.published_at]
    if len(times) < 2:
        return 0.0
    earliest = min(times)
    latest   = max(times)
    hours = (latest - earliest).total_seconds() / 3600
    if hours < 1.0:
        return 0.0
    return min(len(articles) / hours, 20.0)


def compute_novelty(
    db: Session,
    cluster_tickers: list[str],
    cluster_started_at: datetime,
    lookback_hours: int = 48,
) -> float:
    """1.0 si aucun Signal existant sur ces tickers dans la fenêtre, 0.5 sinon."""
    if not cluster_tickers:
        return 1.0
    window_start = cluster_started_at - timedelta(hours=lookback_hours)
    existing = (
        db.query(Signal)
        .filter(
            Signal.created_at >= window_start,
            Signal.created_at < cluster_started_at,
        )
        .all()
    )
    for sig in existing:
        if sig.tickers and any(t in cluster_tickers for t in sig.tickers):
            return 0.5
    return 1.0


def classify_strength(
    volume: int,
    authority: float,
    velocity: float,
    novelty: float,
    has_tier1_source: bool,
) -> str:
    """
    Calibration pour ce dataset (peu volumineux).

    strong : (volume >= 4 AND authority >= 0.45)
             OR (volume >= 3 AND has_tier1_source AND novelty == 1.0)
             OR (volume >= 5 AND velocity >= 1.5)
    medium : (volume >= 2 AND authority >= 0.4) OR (volume >= 3)
    weak   : sinon
    """
    if (
        (volume >= 4 and authority >= 0.45)
        or (volume >= 3 and has_tier1_source and novelty == 1.0)
        or (volume >= 5 and velocity >= 1.5)
    ):
        return "strong"
    if (volume >= 2 and authority >= 0.4) or volume >= 3:
        return "medium"
    return "weak"


def build_signal_summary(articles: list[RawArticle]) -> str:
    """Pré-summary sans LLM : titre le plus long + 3 meilleures sources."""
    longest_title = max((a.title for a in articles), key=len, default="")
    seen: dict[str, int] = {}
    for a in articles:
        if a.source and a.source not in seen:
            seen[a.source] = getattr(a, "source_tier", 3) or 3
    top_sources = ", ".join(
        s for s, _ in sorted(seen.items(), key=lambda x: x[1])[:3]
    )
    return f"{longest_title} — sources: {top_sources}"[:500]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def run(db: Session, lookback_hours: int = 48) -> dict[str, Any]:
    """
    Pipeline principal Stage 2.

    Returns:
        {"articles_processed", "clusters_total", "signals_created",
         "by_strength", "discarded_weak"}
    """
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
    articles = (
        db.query(RawArticle)
        .filter(
            RawArticle.processed_at.is_(None),
            RawArticle.published_at >= cutoff,
            RawArticle.tickers.isnot(None),
        )
        .all()
    )

    if not articles:
        logger.info("Stage 2: no articles to process")
        return {
            "articles_processed": 0,
            "clusters_total":     0,
            "signals_created":    0,
            "by_strength":        {"strong": 0, "medium": 0, "weak": 0},
            "discarded_weak":     0,
        }

    logger.info("Stage 2: processing %d articles", len(articles))

    titles            = [a.title for a in articles]
    embeddings        = embed_titles(titles)
    clusters_by_label = cluster_articles_by_ticker(articles, embeddings)

    signals_created = 0
    by_strength     = {"strong": 0, "medium": 0, "weak": 0}
    discarded_weak  = 0
    clusters_total  = 0

    for label, indices in clusters_by_label.items():
        if label == -1 or len(indices) < _MIN_CLUSTER_SIZE:
            continue
        clusters_total += 1

        cluster_articles = [articles[i] for i in indices]

        try:
            volume    = len(cluster_articles)
            authority = compute_authority(cluster_articles)
            velocity  = compute_velocity(cluster_articles)

            tickers_seen: list[str] = []
            for a in cluster_articles:
                if a.tickers:
                    tickers_seen.extend(a.tickers)
            ticker_primary = (
                Counter(tickers_seen).most_common(1)[0][0] if tickers_seen else None
            )
            tickers_union = sorted(set(tickers_seen))

            cluster_started_at = min(
                (a.published_at for a in cluster_articles if a.published_at),
                default=datetime.utcnow(),
            )
            novelty   = compute_novelty(
                db, [ticker_primary] if ticker_primary else [], cluster_started_at
            )
            has_tier1 = any(a.source_tier == 1 for a in cluster_articles)
            strength  = classify_strength(
                volume, authority, velocity, novelty, has_tier1
            )

            if strength == "weak":
                discarded_weak += 1
                by_strength["weak"] += 1
                continue

            db.add(Signal(
                cluster_id=f"c{label}_{int(datetime.utcnow().timestamp())}",
                strength=strength,
                volume=volume,
                velocity=velocity,
                authority_score=authority,
                novelty_score=novelty,
                summary=build_signal_summary(cluster_articles),
                ticker_primary=ticker_primary,
                tickers=tickers_union,
                status="pending",
            ))
            signals_created += 1
            by_strength[strength] += 1

        except Exception as exc:
            logger.warning(
                "Error processing cluster label=%d: %s — skipping", label, exc
            )

    now = datetime.utcnow()
    for a in articles:
        a.processed_at = now

    db.commit()

    result = {
        "articles_processed": len(articles),
        "clusters_total":     clusters_total,
        "signals_created":    signals_created,
        "by_strength":        by_strength,
        "discarded_weak":     discarded_weak,
    }
    logger.info("Stage 2 complete: %s", result)
    return result
