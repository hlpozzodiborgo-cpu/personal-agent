"""
FastAPI router for the /agent prefix.
"""
from typing import Optional

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from agent.deps import get_db
from agent.schemas import (
    AgentHealthResponse,
    IngestRequest,
    IngestResponse,
    SignalsRunRequest,
    SignalsRunResponse,
    SignalRead,
)
from agent import stage1_ingest, stage2_signals

router = APIRouter(prefix="/agent", tags=["Agent Pipeline"])


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=AgentHealthResponse)
async def get_agent_health() -> AgentHealthResponse:
    """Vérifie que le module agent est correctement initialisé."""
    return AgentHealthResponse(status="ok", stage="stage2")


# ---------------------------------------------------------------------------
# Stage 1 — Ingest
# ---------------------------------------------------------------------------

@router.post("/ingest/run", response_model=IngestResponse)
async def run_ingest(
    lookback_hours: int = 24,
    body: Optional[IngestRequest] = Body(default=None),
    db: Session = Depends(get_db),
) -> IngestResponse:
    """
    Déclenche l'ingestion multi-sources pour la fenêtre temporelle donnée.

    Query params:
        lookback_hours: nombre d'heures à remonter (défaut 24)
    Body (optionnel):
        tickers: liste de symboles à cibler (ex: ["AAPL", "MC.PA"])
    """
    portfolio_symbols = body.tickers if body else None
    result = await stage1_ingest.run(
        db, portfolio_symbols=portfolio_symbols, lookback_hours=lookback_hours
    )
    return IngestResponse(**result)


# ---------------------------------------------------------------------------
# Stage 2 — Signals
# ---------------------------------------------------------------------------

@router.post("/signals/run", response_model=SignalsRunResponse)
async def run_signals(
    req: SignalsRunRequest,
    db: Session = Depends(get_db),
) -> SignalsRunResponse:
    """
    Clusterise les articles non-traités et génère des Signals.

    Body:
        lookback_hours: fenêtre temporelle (défaut 48h)
    """
    result = await stage2_signals.run(db, lookback_hours=req.lookback_hours)
    return SignalsRunResponse(**result)


@router.get("/signals", response_model=list[SignalRead])
async def list_signals(
    strength: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[SignalRead]:
    """
    Liste les Signals générés, optionnellement filtrés par strength.

    Query params:
        strength: weak | medium | strong (optionnel)
        limit:    nombre max de résultats (défaut 50)
    """
    from agent.models import Signal

    q = db.query(Signal).order_by(Signal.created_at.desc())
    if strength:
        q = q.filter(Signal.strength == strength)
    return q.limit(limit).all()
