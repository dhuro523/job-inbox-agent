"""
Database engine and session management.

Why this exists as its own module: every part of the app that touches
the database (ingestion, matching, agent tools, API) needs a session,
but none of them should know HOW the connection is configured. This is
the single place that knows about the DATABASE_URL and connection pooling.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Check your .env file."
    )

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db_session():
    """
    Yields a database session, ensuring it's closed afterward.
    This generator pattern will plug directly into FastAPI's dependency
    injection system in Phase 10.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()