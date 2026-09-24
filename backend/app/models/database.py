"""Database models and session management for RSTAM."""
import uuid
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

Base = declarative_base()

# Module-level engine and session factory
_engine = None
_SessionLocal = None


class Case(Base):
    """Represents a victim/complainant case."""
    __tablename__ = "cases"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = Column(String, nullable=False)
    language = Column(String, nullable=False, default="en")
    status = Column(String, nullable=False, default="NEW")
    consent_status = Column(String, nullable=False, default="PENDING")
    consent_granted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    assessments = relationship("Assessment", back_populates="case")


class Assessment(Base):
    """Stores assessment results including SVI scores."""
    __tablename__ = "assessments"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False)
    svi_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    auto_escalated = Column(Boolean, default=False)
    escalation_reason = Column(String, nullable=True)
    voice_transcript = Column(Text, nullable=True)
    original_text = Column(Text, nullable=True)
    translated_text = Column(Text, nullable=True)
    acoustic_features_json = Column(Text, nullable=True)
    emotion_scores_json = Column(Text, nullable=True)
    trauma_keywords_json = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    suicidal_ideation_flag = Column(Boolean, default=False)
    suicidal_ideation_confidence = Column(Float, nullable=True)
    components_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="assessments")
    interventions = relationship("InterventionRecord", back_populates="assessment")


class InterventionRecord(Base):
    """Tracks recommended and dispatched interventions."""
    __tablename__ = "intervention_records"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False)
    intervention_type = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    action_details = Column(String, nullable=False)
    response_sla = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dispatched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    assessment = relationship("Assessment", back_populates="interventions")


class AuditLog(Base):
    """Encrypted audit trail for all system actions."""
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=True)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    details_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_engine(database_url: str = None):
    """Get or create the database engine."""
    global _engine
    if database_url:
        _engine = create_engine(database_url, connect_args={"check_same_thread": False})
    return _engine


def init_db(database_url: str):
    """Initialize the database and create all tables."""
    global _engine, _SessionLocal
    _engine = create_engine(database_url, connect_args={"check_same_thread": False})
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    """Create a new database session."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()
