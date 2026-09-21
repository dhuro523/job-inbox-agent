"""
SQLAlchemy model for the `emails` table.

This table is the source-of-truth audit trail: one row per Gmail message
we've ingested. The UNIQUE constraint on gmail_message_id is what makes
ingestion idempotent at the database level — even safer than our
application-level check in Phase 3, since it's enforced atomically by
Postgres itself.
"""

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database.session import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)
    gmail_message_id = Column(String, unique=True, nullable=False, index=True)
    thread_id = Column(String, nullable=False)
    sender = Column(Text, nullable=False)
    subject = Column(Text)
    received_at = Column(DateTime(timezone=True))
    snippet = Column(Text)
    body_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())