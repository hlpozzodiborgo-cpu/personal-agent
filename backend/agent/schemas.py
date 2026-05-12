"""
Pydantic v2 schemas for the agent pipeline.

Pattern mirrors backend/schemas.py:
  <Entity>Base  — shared fields
  <Entity>Create — fields required on creation (no id/timestamps)
  <Entity>       — full read schema with id and computed fields
  from_attributes = True in Config (Pydantic v2 ORM mode)
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# RawArticle
# ---------------------------------------------------------------------------

class RawArticleBase(BaseModel):
    source:        str
    source_tier:   int = Field(default=3, ge=1, le=5)
    url:           str
    title:         str
    content:       Optional[str] = None
    published_at:  Optional[datetime] = None
    tickers:       Optional[List[str]] = None
    event_type:    Optional[str] = None
    raw_sentiment: Optional[float] = Field(default=None, ge=-1.0, le=1.0)

class RawArticleCreate(RawArticleBase):
    pass

class RawArticle(RawArticleBase):
    id:         int
    fetched_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------------

class SignalBase(BaseModel):
    cluster_id:      Optional[str] = None
    strength:        str = "weak"          # weak | medium | strong
    volume:          int = 0
    velocity:        Optional[float] = None
    authority_score: Optional[float] = None
    novelty_score:   Optional[float] = None
    summary:         Optional[str] = None
    ticker_primary:  Optional[str] = None
    tickers:         Optional[List[str]] = None

class SignalCreate(SignalBase):
    pass

class Signal(SignalBase):
    id:         int
    created_at: datetime
    status:     str                        # pending | escalated | discarded

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Thesis
# ---------------------------------------------------------------------------

class ThesisBase(BaseModel):
    signal_id:               int
    direction:               str = "none"  # long | short | none
    mechanism:               Optional[str] = None
    horizon_days:            Optional[int] = None
    magnitude_pct:           Optional[float] = None
    conviction:              Optional[int] = Field(default=None, ge=0, le=100)
    invalidation_conditions: Optional[List[str]] = None
    llm_reasoning:           Optional[str] = None

class ThesisCreate(ThesisBase):
    pass

class Thesis(ThesisBase):
    id:         int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# QuantCheck
# ---------------------------------------------------------------------------

class QuantCheckBase(BaseModel):
    thesis_id:         int
    valuation_verdict: Optional[str] = None   # bullish | bearish | neutral
    technical_verdict: Optional[str] = None
    factor_verdict:    Optional[str] = None
    analog_outcome:    Optional[str] = None
    agreement:         Optional[str] = None   # confirms | contradicts | neutral
    details:           Optional[Dict[str, Any]] = None

class QuantCheckCreate(QuantCheckBase):
    pass

class QuantCheck(QuantCheckBase):
    id:         int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# RiskAssessment
# ---------------------------------------------------------------------------

class RiskAssessmentBase(BaseModel):
    thesis_id:                int
    expected_drawdown_pct:    Optional[float] = None
    beta:                     Optional[float] = None
    correlation_to_portfolio: Optional[float] = None
    liquidity_ok:             Optional[bool] = None
    suggested_size_pct:       Optional[float] = None
    scenarios:                Optional[Dict[str, Any]] = None

class RiskAssessmentCreate(RiskAssessmentBase):
    pass

class RiskAssessment(RiskAssessmentBase):
    id:         int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------------

class RecommendationBase(BaseModel):
    thesis_id:       int
    action:          str                   # buy | sell | hold | watch
    instrument_type: str = "etf"           # stock | etf | crypto | other
    ticker:          str
    size_pct:        Optional[float] = None
    rationale_fr:    Optional[str] = None
    rationale_en:    Optional[str] = None

class RecommendationCreate(RecommendationBase):
    pass

class Recommendation(RecommendationBase):
    id:          int
    status:      str                       # active | closed | invalidated
    created_at:  datetime
    closed_at:   Optional[datetime] = None
    outcome_pct: Optional[float] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# SourceWeight
# ---------------------------------------------------------------------------

class SourceWeightBase(BaseModel):
    source_name:    str
    tier:           int = Field(default=3, ge=1, le=5)
    current_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    hits:           int = 0
    misses:         int = 0

class SourceWeightCreate(SourceWeightBase):
    pass

class SourceWeight(SourceWeightBase):
    id:           int
    last_updated: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Pipeline responses
# ---------------------------------------------------------------------------

class AgentHealthResponse(BaseModel):
    status: str
    stage:  str

class PipelineRunResponse(BaseModel):
    articles_ingested:      int
    signals_created:        int
    theses_generated:       int
    recommendations_ready:  int
    errors:                 List[str] = []

class IngestRequest(BaseModel):
    tickers: Optional[List[str]] = None

class IngestResponse(BaseModel):
    fetched:      int
    after_dedupe: int
    persisted:    int
    per_source:   Dict[str, int] = {}
