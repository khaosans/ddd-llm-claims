"""
SQLAlchemy Database Models

These models represent the database schema for persistent storage.
They map domain objects to database tables.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

try:
    from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        Enum,
        ForeignKey,
        Integer,
        Numeric,
        String,
        Text,
        Float,
        JSON,
        create_engine,
    )
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship, sessionmaker
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Create dummy classes for when SQLAlchemy is not available
    class Base:
        pass
    def create_engine(*args, **kwargs):
        raise ImportError("SQLAlchemy not installed. Install with: pip install sqlalchemy")


class ClaimModel(Base):
    """Database model for Claim aggregate"""
    __tablename__ = "claims"
    
    claim_id = Column(String(36), primary_key=True)  # UUID as string
    raw_input = Column(Text, nullable=False)
    source = Column(String(50), nullable=False, default="email")
    status = Column(String(50), nullable=False, default="draft")
    
    # ClaimSummary fields (flattened for simplicity)
    claim_type = Column(String(50))
    incident_date = Column(DateTime)
    reported_date = Column(DateTime)
    claimed_amount = Column(Numeric(15, 2))
    currency = Column(String(10), default="USD")
    incident_location = Column(Text)
    description = Column(Text)
    claimant_name = Column(String(200))
    claimant_email = Column(String(200))
    claimant_phone = Column(String(50))
    policy_number = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("ReviewModel", back_populates="claim")
    events = relationship("EventModel", back_populates="claim")


class PolicyModel(Base):
    """Database model for Policy aggregate"""
    __tablename__ = "policies"
    
    policy_id = Column(String(36), primary_key=True)  # UUID as string
    policy_number = Column(String(100), unique=True, nullable=False)
    customer_id = Column(String(36), nullable=False)
    status = Column(String(50), nullable=False)
    policy_type = Column(String(50))
    coverage_start = Column(DateTime)
    coverage_end = Column(DateTime)
    max_coverage_amount = Column(Numeric(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReviewModel(Base):
    """Database model for Review items"""
    __tablename__ = "reviews"
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(36), ForeignKey("claims.claim_id"), nullable=False)
    priority = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False)
    ai_decision = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    assigned_to = Column(String(100))
    human_decision = Column(String(20))
    human_feedback = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    # Relationships (only if SQLAlchemy available)
    if SQLALCHEMY_AVAILABLE:
        claim = relationship("ClaimModel", back_populates="reviews")


class EventModel(Base):
    """Database model for Domain Events (Event Sourcing)"""
    __tablename__ = "events"
    
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(36), ForeignKey("claims.claim_id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(Text, nullable=False)  # JSON string
    occurred_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships (only if SQLAlchemy available)
    if SQLALCHEMY_AVAILABLE:
        claim = relationship("ClaimModel", back_populates="events")


class DecisionAuditModel(Base):
    """Database model for Decision Audit records"""
    __tablename__ = "decision_audits"
    
    decision_id = Column(String(36), primary_key=True)  # UUID as string
    claim_id = Column(String(36), ForeignKey("claims.claim_id"), nullable=False)
    agent_component = Column(String(100), nullable=False)
    decision_type = Column(String(50), nullable=False)
    decision_value = Column(Text, nullable=False)  # JSON string
    reasoning = Column(Text, nullable=False)
    confidence = Column(Float)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    workflow_step = Column(String(100))
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    if SQLALCHEMY_AVAILABLE:
        claim = relationship("ClaimModel", back_populates="decisions")
        context = relationship("DecisionContextModel", back_populates="decision", uselist=False)
        dependencies = relationship("DecisionDependencyModel", back_populates="decision")
        explanations = relationship("ExplanationModel", back_populates="decision")


class DecisionContextModel(Base):
    """Database model for Decision Context"""
    __tablename__ = "decision_contexts"
    
    context_id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(String(36), ForeignKey("decision_audits.decision_id"), nullable=False, unique=True)
    
    # Store as JSON for flexibility
    inputs = Column(Text)  # JSON string
    prompts = Column(Text)
    llm_response = Column(Text)
    intermediate_steps = Column(Text)  # JSON string
    evidence = Column(Text)  # JSON string
    metadata = Column(Text)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    if SQLALCHEMY_AVAILABLE:
        decision = relationship("DecisionAuditModel", back_populates="context")


class DecisionDependencyModel(Base):
    """Database model for Decision Dependencies"""
    __tablename__ = "decision_dependencies"
    
    dependency_id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(String(36), ForeignKey("decision_audits.decision_id"), nullable=False)
    depends_on_decision_id = Column(String(36), nullable=False)
    dependency_type = Column(String(50), nullable=False)
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    if SQLALCHEMY_AVAILABLE:
        decision = relationship("DecisionAuditModel", back_populates="dependencies")


class ExplanationModel(Base):
    """Database model for Explanations"""
    __tablename__ = "explanations"
    
    explanation_id = Column(String(36), primary_key=True)  # UUID as string
    decision_id = Column(String(36), ForeignKey("decision_audits.decision_id"), nullable=False)
    level = Column(String(20), nullable=False)  # summary, detailed, regulatory, debug
    content = Column(Text, nullable=False)
    format = Column(String(20), default="text")
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    if SQLALCHEMY_AVAILABLE:
        decision = relationship("DecisionAuditModel", back_populates="explanations")


class DocumentModel(Base):
    """Database model for Document Value Objects"""
    __tablename__ = "documents"
    
    document_id = Column(String(36), primary_key=True)  # UUID as string
    claim_id = Column(String(36), ForeignKey("claims.claim_id"), nullable=False)
    document_type = Column(String(50), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 hash
    status = Column(String(20), nullable=False, default="pending")
    authenticity_score = Column(Float)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    validated_at = Column(DateTime)
    
    # Metadata fields (stored as JSON for flexibility)
    metadata_json = Column(Text)  # JSON string of DocumentMetadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    if SQLALCHEMY_AVAILABLE:
        claim = relationship("ClaimModel", back_populates="documents")
        validations = relationship("DocumentValidationModel", back_populates="document")


class DocumentValidationModel(Base):
    """Database model for Document Validation records"""
    __tablename__ = "document_validations"
    
    validation_id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey("documents.document_id"), nullable=False)
    validation_type = Column(String(50), nullable=False)  # e.g., "compliance", "authenticity", "analysis"
    passed = Column(Boolean, nullable=False)
    details = Column(Text)  # JSON string with validation details
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    if SQLALCHEMY_AVAILABLE:
        document = relationship("DocumentModel", back_populates="validations")


# Update ClaimModel to include documents and decisions relationships
if SQLALCHEMY_AVAILABLE:
    # Add decisions relationship to ClaimModel
    ClaimModel.decisions = relationship("DecisionAuditModel", back_populates="claim")
    # Add documents relationship to ClaimModel
    ClaimModel.documents = relationship("DocumentModel", back_populates="claim")


def get_engine(db_path: str = "data/claims.db"):
    """Get SQLAlchemy engine"""
    if not SQLALCHEMY_AVAILABLE:
        raise ImportError("SQLAlchemy not installed. Install with: pip install sqlalchemy")
    import os
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session_factory(db_path: str = "data/claims.db"):
    """Get session factory"""
    engine = get_engine(db_path)
    return sessionmaker(bind=engine)

