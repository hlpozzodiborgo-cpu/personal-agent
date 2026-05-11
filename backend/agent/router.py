"""
FastAPI router for the /agent prefix.
"""
from typing import Optional

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from agent.deps import get_db
from agent.schemas import AgentHealthResponse, IngestRequest, IngestResponse
from agent import stage1_ingest

router = APIRouter(prefix="/agent", tags=["Agent Pipeline"])


@router.get("/health", response_model=AgentHealthResponse)
async def get_agent_health() -> AgentHealthResponse:
    """Vérifie que le module agent est correctement initialisé."""
    return AgentHealthResponse(status="ok", stage="stage1")


@router.post("/ingest/run", response_model=IngestResponse)
async def run_ingest(
    lookback_hours: int = 24,
    body: Optional[IngestRequest] = Body(default=None),
    db: Session = Depends(get_db),
) -> IngestResponse:
    """
    Déclenche l'ingestion GDELT pour la fenêtre temporelle donnée.

    Query params:
        lookback_hours: nombre d'heures à remonter (défaut 24)
    Body (optionnel):
        tickers: liste de symboles à cibler (ex: ["AAPL", "MC.PA"])
    """
    portfolio_symbols = body.tickers if body else None
    result = await stage1_ingest.run(db, portfolio_symbols=portfolio_symbols, lookback_hours=lookback_hours)
    return IngestResponse(**result)
