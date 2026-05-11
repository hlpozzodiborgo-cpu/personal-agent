"""
Standalone DB session factory for the agent module.

Uses the same DATABASE_URL as the rest of the app but creates its own
engine to avoid circular imports with main.py (which also defines get_db).
Pattern mirrors routes_news.py.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
_Session = sessionmaker(bind=_engine)


def get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()
