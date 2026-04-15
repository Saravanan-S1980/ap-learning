"""SQLAlchemy ORM models + async engine / session factory."""
import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


class ExtractionRecord(Base):
    __tablename__ = "extractions"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    lab_name = Column(String, nullable=True)
    report_date = Column(String, nullable=True)
    extraction_confidence = Column(Float, default=0.0)
    raw_json = Column(Text, nullable=True)   # JSON list of ExtractedMarker dicts
    marker_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProtocolRecord(Base):
    __tablename__ = "protocols"

    id = Column(String, primary_key=True)
    extraction_id = Column(String, nullable=False)
    goals = Column(Text, nullable=True)         # JSON list of goal IDs
    protocol_json = Column(Text, nullable=True)
    # Denormalised from ExtractionRecord for cheap listing queries
    lab_name = Column(String, nullable=True)
    report_date = Column(String, nullable=True)
    marker_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Async engine & session factory ───────────────────────────────────────────

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db() -> None:
    """Create all tables if they don't already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
