"""
SQLAlchemy model for the `application_events` table.

This table is what makes the system's reasoning traceable: every event
links back to the exact email it came from, and every application's
status is derived from its events — never set arbitrarily. This is the
lineage chain: application status -> event -> source email.
"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.database.session import Base


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True)
    application_id = Column(
        Integer, ForeignKey("applications.id"), nullable=False, index=True
    )
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    event_type = Column(String, nullable=False)
    event_date = Column(DateTime(timezone=True))
    description = Column(Text)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())