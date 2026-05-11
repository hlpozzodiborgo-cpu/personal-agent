# Investor AI — CLAUDE.md

Reference document for AI-assisted development on this repository.
Read this before writing any code.

---

## Stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Backend   | Python 3.9+ · FastAPI · SQLAlchemy 1.x · SQLite |
| Frontend  | Next.js 14 · React 18 · Tailwind CSS · Recharts |
| AI        | Anthropic Claude / Google Gemini / Groq (Llama) |
| Data      | Yahoo Finance (direct API) · Finnhub · NewsAPI  |
| Auth      | None (local single-user app)                    |

---

## Folder structure

```
Investor AI/
├── backend/
│   ├── main.py              # FastAPI app, DB init, startup key loading
│   ├── models.py            # SQLAlchemy ORM — Phase 1 tables
│   ├── schemas.py           # Pydantic v2 schemas — Phase 1
│   ├── crud.py              # Static-method CRUD classes
│   ├── config.py            # ENV vars (DATABASE_URL, API keys)
│   ├── finance_service.py   # Price fetching (Finnhub → Yahoo → mock)
│   ├── ai_service.py        # Multi-provider LLM (Claude / Gemini / Groq)
│   ├── news_service.py      # NewsAPI article fetching
│   ├── routes_news.py       # /api/news/* router (Phase 2 v1)
│   └── agent/               # Phase 2/3 multi-stage agent (NEW)
│       ├── __init__.py
│       ├── models.py        # Agent SQLAlchemy models (own Base)
│       ├── schemas.py       # Agent Pydantic schemas
│       ├── router.py        # /agent/* FastAPI router
│       ├── pipeline.py      # Stage orchestrator
│       ├── stage1_ingest.py
│       ├── stage2_signals.py
│       ├── stage3_analyze.py
│       ├── stage4_thesis.py
│       ├── stage5_quant.py
│       ├── stage6_risk.py
│       ├── stage7_recommend.py
│       ├── sources/         # Source adapters (RSS, NewsAPI, Finnhub…)
│       └── prompts/         # LLM prompt templates
├── frontend/
│   ├── app/
│   │   ├── page.jsx         # Main dashboard page
│   │   └── globals.css
│   ├── components/
│   │   ├── PortfolioComponents.jsx
│   │   ├── Modals.jsx
│   │   └── NewsRecommendations.jsx
│   └── lib/
│       ├── api.js           # Axios wrappers for all backend calls
│       └── utils.js         # formatCurrency, formatPercent, color helpers
└── CLAUDE.md
```

---

## What Phase 1 already does

- **Asset tracking**: add/remove symbols (stocks, ETFs, crypto, forex) via Yahoo Finance search
- **Portfolio positions**: record purchases with historical price auto-fetch (date → closing price via Yahoo Finance chart API)
- **TWR calculation**: Time-Weighted Return per period, excluding cash-flow effects; portfolio history reconstructed day-by-day from market prices
- **Multi-period charts**: 1J/1S/1M/1A/Tout with comparison curves (any asset, normalized to same baseline); Recharts AreaChart with gradient
- **Live prices**: Finnhub (US stocks) → Yahoo Finance direct API (EU ETFs) → mock fallback; 10-min in-memory cache
- **Settings**: per-key API management (Finnhub, Anthropic, Gemini, Groq, NewsAPI) stored in `app_settings` SQLite table; preferences (risk appetite 1-5, investment horizon)
- **Phase 2 v1**: basic news fetch (NewsAPI) + LLM analysis (Claude/Gemini/Groq) returning structured JSON per article; `routes_news.py` / `ai_service.py`

---

## Database: migration approach

**No Alembic.** Migrations are handled two ways:
1. New tables: `Base.metadata.create_all(bind=engine)` at startup — creates any table that does not yet exist.
2. New columns on existing tables: manual `ALTER TABLE … ADD COLUMN …` in `main.py`, wrapped in try/except to be idempotent.

The agent module uses its own `AgentBase = declarative_base()` so its tables are created independently via `AgentBase.metadata.create_all(bind=engine)` without touching the Phase 1 tables.

---

## Naming conventions (observed in existing code)

| Concern | Convention | Example |
|---|---|---|
| Python files | `snake_case` | `finance_service.py` |
| SQLAlchemy models | `PascalCase` | `class RawArticle(AgentBase)` |
| Table names | `snake_case` plural | `raw_articles` |
| CRUD classes | `PascalCase` + `CRUD` suffix, static methods | `class SignalCRUD` |
| FastAPI routes | `snake_case` functions | `async def get_agent_health()` |
| Pydantic schemas | Base → Create → Read pattern | `SignalBase`, `SignalCreate`, `Signal` |
| Pydantic config | `from_attributes = True` (Pydantic v2) | inside `class Config` |
| React components | `PascalCase`, named exports | `export const HoldingsList` |
| React hooks | `useState`, `useEffect`, `useMemo` at top | before JSX |
| API functions | `camelCase` | `getPortfolioHistory` |

---

## Language conventions

| Location | Language |
|---|---|
| User-facing strings (UI labels, error messages returned to client) | **French** |
| Code: variable names, function names, class names | **English** |
| Python docstrings | French (matching existing style) |
| Comments inside functions | French (matching existing style) |
| CLAUDE.md, CRUD docstrings (new code) | Either — prefer English for new agent code |

---

## The 7-stage agent funnel (Phase 2/3)

```
Stage 1 — Ingest
  Collect raw articles from multiple sources (NewsAPI, RSS, Finnhub,
  Reddit, SEC EDGAR…). Deduplicate by URL. Store as RawArticle.
  Assign source_tier (1=premium, 5=low-quality).

Stage 2 — Broad scan & signal detection
  Cluster articles by topic/ticker. Compute volume, velocity,
  authority_score, novelty_score. Promote clusters to Signal
  when thresholds are crossed (strength: weak/medium/strong).

Stage 3 — Deep read & analysis
  For each escalated Signal: deep LLM read of full article content.
  Extract event type, quantitative data, management sentiment.
  Cross-reference against user portfolio positions.

Stage 4 — Thesis generation
  LLM generates an investment thesis: direction (long/short/none),
  mechanism (why price should move), horizon_days, magnitude_pct,
  conviction 0-100, invalidation conditions. Stored as Thesis.

Stage 5 — Quantitative verification
  Independent checks against the thesis: valuation (P/E vs peers),
  technical (trend, momentum), factor (value/quality/growth),
  historical analogs. Verdict: confirms / contradicts / neutral.

Stage 6 — Risk assessment
  Given the thesis and user portfolio: expected drawdown, beta,
  correlation to existing holdings, liquidity check, position sizing.
  Output: suggested_size_pct and scenario analysis (bull/base/bear).

Stage 7 — Recommendation
  Synthesise Thesis + QuantCheck + RiskAssessment into a
  Recommendation. Generate rationale in French (rationale_fr)
  and English (rationale_en). Status: active / closed / invalidated.
```

---

## DO NOT TOUCH

- `backend/models.py` — existing Phase 1 tables (Asset, Holding, Transaction, PriceHistory, AppSetting, PortfolioSnapshot)
- `backend/schemas.py` — existing Phase 1 Pydantic schemas
- `backend/crud.py` — existing CRUD classes (AssetCRUD, HoldingCRUD, TransactionCRUD, PriceHistoryCRUD)
- `backend/finance_service.py` — price fetching logic, cache, mock data
- All existing frontend components and API routes
- Existing SQLite tables (never `DROP TABLE`, never remove columns)

Additions to `backend/main.py` must be surgical: import the agent router and call `AgentBase.metadata.create_all()`. Nothing else.

---

## Agent module: key design decisions

- **Isolated Base**: `AgentBase = declarative_base()` in `agent/models.py`. Never import from Phase 1 `models.py`.
- **JSON columns**: use `sqlalchemy.JSON` for list/dict fields (SQLite stores as text, SQLAlchemy handles serialisation).
- **String enums**: use plain `String` columns with docstring listing valid values (matches existing codebase; no SQLAlchemy `Enum` type to avoid migration complexity).
- **FKs stay inside agent**: `Thesis.signal_id → signals.id`, etc. No FK to Phase 1 tables.
- **Async-friendly stubs**: stage functions are `async def` to allow future parallelism.
