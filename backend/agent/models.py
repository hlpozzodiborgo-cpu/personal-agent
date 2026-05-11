"""
SQLAlchemy models for the Phase 2/3 agent pipeline.

Uses a separate AgentBase so these tables are created independently
from the Phase 1 tables (Asset, Holding, …) in models.py.

String-based enums match the existing codebase style (no SQLAlchemy Enum
type) — valid values are documented in each column comment.
JSON columns are stored as text by SQLite; SQLAlchemy handles serialisation.

DO NOT import from backend/models.py — keep agent tables fully isolated.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    ForeignKey, Text, JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

AgentBase = declarative_base()


# ---------------------------------------------------------------------------
# Stage 1 — Ingest
# ---------------------------------------------------------------------------

class RawArticle(AgentBase):
    """
    Un article brut collecté depuis une source externe.

    source_tier: 1 (premium — Bloomberg, FT) → 5 (faible — Reddit, blog)
    event_type:  earnings | macro | regulatory | m_and_a | product | other
    raw_sentiment: score flottant [-1, 1] calculé par heuristique rapide
    tickers: liste JSON de symboles mentionnés (ex: ["AAPL", "MSFT"])
    """
    __tablename__ = "raw_articles"

    id           = Column(Integer, primary_key=True, index=True)
    source       = Column(String, nullable=False, index=True)
    source_tier  = Column(Integer, nullable=False, default=3)   # 1–5
    url          = Column(String, unique=True, nullable=False, index=True)
    title        = Column(Text, nullable=False)
    content      = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    fetched_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    tickers      = Column(JSON, nullable=True)                   # list[str]
    event_type   = Column(String, nullable=True)
    raw_sentiment= Column(Float, nullable=True)                  # [-1, 1]


# ---------------------------------------------------------------------------
# Stage 2 — Signal detection
# ---------------------------------------------------------------------------

class Signal(AgentBase):
    """
    Cluster d'articles convergents autour d'un même sujet/ticker.

    strength:  weak | medium | strong
    status:    pending | escalated | discarded
    tickers:   list JSON de tous les tickers concernés
    """
    __tablename__ = "signals"

    id              = Column(Integer, primary_key=True, index=True)
    cluster_id      = Column(String, nullable=True, index=True)  # opaque group key
    strength        = Column(String, nullable=False, default="weak")
    volume          = Column(Integer, nullable=False, default=0)  # nb articles
    velocity        = Column(Float, nullable=True)                # articles/hour
    authority_score = Column(Float, nullable=True)               # 0–1
    novelty_score   = Column(Float, nullable=True)               # 0–1
    summary         = Column(Text, nullable=True)                 # LLM-generated
    ticker_primary  = Column(String, nullable=True, index=True)
    tickers         = Column(JSON, nullable=True)                 # list[str]
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
    status          = Column(String, nullable=False, default="pending")

    # Relations
    theses          = relationship("Thesis", back_populates="signal",
                                   cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Stage 4 — Thesis
# ---------------------------------------------------------------------------

class Thesis(AgentBase):
    """
    Thèse d'investissement générée par LLM à partir d'un Signal.

    direction:              long | short | none
    conviction:             0–100
    invalidation_conditions: list JSON de conditions qui invalident la thèse
    """
    __tablename__ = "theses"

    id                     = Column(Integer, primary_key=True, index=True)
    signal_id              = Column(Integer, ForeignKey("signals.id"),
                                    nullable=False, index=True)
    direction              = Column(String, nullable=False, default="none")
    mechanism              = Column(Text, nullable=True)
    horizon_days           = Column(Integer, nullable=True)
    magnitude_pct          = Column(Float, nullable=True)
    conviction             = Column(Integer, nullable=True)         # 0–100
    invalidation_conditions= Column(JSON, nullable=True)            # list[str]
    llm_reasoning          = Column(Text, nullable=True)
    created_at             = Column(DateTime, default=datetime.utcnow,
                                    nullable=False)

    # Relations
    signal                 = relationship("Signal", back_populates="theses")
    quant_check            = relationship("QuantCheck", back_populates="thesis",
                                          uselist=False,
                                          cascade="all, delete-orphan")
    risk_assessment        = relationship("RiskAssessment",
                                          back_populates="thesis",
                                          uselist=False,
                                          cascade="all, delete-orphan")
    recommendation         = relationship("Recommendation",
                                          back_populates="thesis",
                                          uselist=False,
                                          cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Stage 5 — Quantitative verification
# ---------------------------------------------------------------------------

class QuantCheck(AgentBase):
    """
    Vérification quantitative indépendante d'une Thesis.

    valuation_verdict:  bullish | bearish | neutral
    technical_verdict:  bullish | bearish | neutral
    factor_verdict:     bullish | bearish | neutral
    agreement:          confirms | contradicts | neutral
    details:            dict JSON avec métriques brutes (P/E, RSI, …)
    """
    __tablename__ = "quant_checks"

    id                = Column(Integer, primary_key=True, index=True)
    thesis_id         = Column(Integer, ForeignKey("theses.id"),
                               nullable=False, unique=True, index=True)
    valuation_verdict = Column(String, nullable=True)
    technical_verdict = Column(String, nullable=True)
    factor_verdict    = Column(String, nullable=True)
    analog_outcome    = Column(Text, nullable=True)
    agreement         = Column(String, nullable=True)              # confirms | contradicts | neutral
    details           = Column(JSON, nullable=True)               # dict
    created_at        = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    thesis            = relationship("Thesis", back_populates="quant_check")


# ---------------------------------------------------------------------------
# Stage 6 — Risk assessment
# ---------------------------------------------------------------------------

class RiskAssessment(AgentBase):
    """
    Analyse de risque pour une Thesis, calibrée au portefeuille utilisateur.

    scenarios: dict JSON {bull: {…}, base: {…}, bear: {…}}
    """
    __tablename__ = "risk_assessments"

    id                      = Column(Integer, primary_key=True, index=True)
    thesis_id               = Column(Integer, ForeignKey("theses.id"),
                                     nullable=False, unique=True, index=True)
    expected_drawdown_pct   = Column(Float, nullable=True)
    beta                    = Column(Float, nullable=True)
    correlation_to_portfolio= Column(Float, nullable=True)          # -1 to 1
    liquidity_ok            = Column(Boolean, nullable=True)
    suggested_size_pct      = Column(Float, nullable=True)          # % of portfolio
    scenarios               = Column(JSON, nullable=True)           # dict
    created_at              = Column(DateTime, default=datetime.utcnow,
                                     nullable=False)

    # Relations
    thesis                  = relationship("Thesis",
                                           back_populates="risk_assessment")


# ---------------------------------------------------------------------------
# Stage 7 — Recommendation
# ---------------------------------------------------------------------------

class Recommendation(AgentBase):
    """
    Recommandation finale produite par le pipeline.

    action:          buy | sell | hold | watch
    instrument_type: stock | etf | crypto | other
    status:          active | closed | invalidated
    outcome_pct:     rendement réalisé à la clôture (null si toujours active)
    """
    __tablename__ = "recommendations"

    id              = Column(Integer, primary_key=True, index=True)
    thesis_id       = Column(Integer, ForeignKey("theses.id"),
                             nullable=False, unique=True, index=True)
    action          = Column(String, nullable=False)                # buy|sell|hold|watch
    instrument_type = Column(String, nullable=False, default="etf")
    ticker          = Column(String, nullable=False, index=True)
    size_pct        = Column(Float, nullable=True)
    rationale_fr    = Column(Text, nullable=True)
    rationale_en    = Column(Text, nullable=True)
    status          = Column(String, nullable=False, default="active")
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at       = Column(DateTime, nullable=True)
    outcome_pct     = Column(Float, nullable=True)

    # Relations
    thesis          = relationship("Thesis", back_populates="recommendation")


# ---------------------------------------------------------------------------
# Meta — Source reliability tracking
# ---------------------------------------------------------------------------

class SourceWeight(AgentBase):
    """
    Suivi de la fiabilité de chaque source au fil du temps.

    tier: 1 (premium) → 5 (faible qualité)
    current_weight: 0–1, ajusté après chaque Recommendation clôturée
    hits:   nombre de recommandations correctes issues de cette source
    misses: nombre de recommandations incorrectes
    """
    __tablename__ = "source_weights"

    id             = Column(Integer, primary_key=True, index=True)
    source_name    = Column(String, unique=True, nullable=False, index=True)
    tier           = Column(Integer, nullable=False, default=3)    # 1–5
    current_weight = Column(Float, nullable=False, default=1.0)   # 0–1
    hits           = Column(Integer, nullable=False, default=0)
    misses         = Column(Integer, nullable=False, default=0)
    last_updated   = Column(DateTime, default=datetime.utcnow, nullable=False)
