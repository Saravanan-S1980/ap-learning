# SQLAlchemy ORM models — placeholder
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ExtractionRecord(Base):
    __tablename__ = "extractions"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    lab_name = Column(String, nullable=True)
    report_date = Column(String, nullable=True)
    extraction_confidence = Column(Float, default=0.0)
    raw_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProtocolRecord(Base):
    __tablename__ = "protocols"

    id = Column(String, primary_key=True)
    extraction_id = Column(String, nullable=False)
    goals = Column(Text, nullable=True)   # JSON list
    protocol_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
