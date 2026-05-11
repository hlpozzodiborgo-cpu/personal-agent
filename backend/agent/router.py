"""
FastAPI router for the /agent prefix.

Currently exposes only the scaffold health endpoint.
Additional endpoints will be added as each stage is implemented.
"""
from fastapi import APIRouter
from agent.schemas import AgentHealthResponse

router = APIRouter(prefix="/agent", tags=["Agent Pipeline"])


@router.get("/health", response_model=AgentHealthResponse)
async def get_agent_health() -> AgentHealthResponse:
    """Vérifie que le module agent est correctement initialisé."""
    return AgentHealthResponse(status="ok", stage="scaffold")
