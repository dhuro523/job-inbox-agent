"""
SQLAlchemy model for the `applications` table.

One row per real-world job application — this is the entity the user
thinks in terms of ("my Mercor application"), aggregated from one or
more source emails via application_events.
"""

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text, func

from app.database.session import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    company = Column(Text, nullable=False, index=True)
    role = Column(Text, nullable=False)
    location = Column(Text)
    source = Column(Text)
    application_date = Column(Date)
    current_status = Column(String, nullable=False, default="UNKNOWN")
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )