"""
Database-backed Policy Repository

Replaces in-memory repository with SQLite persistence.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..domain.policy import Policy, PolicyStatus
from ..repositories.policy_repository import PolicyRepository
from ..database.models import PolicyModel
from ..database.session import get_db_session


class DatabasePolicyRepository(PolicyRepository):
    """
    Database-backed implementation of PolicyRepository.
    
    Uses SQLAlchemy to persist policies to SQLite database.
    """
    
    def __init__(self, db_path: str = "data/claims.db"):
        """
        Initialize the database repository.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
        from ..database.session import init_db
        init_db(db_path)
    
    def _to_domain(self, db_model: PolicyModel) -> Policy:
        """Convert database model to domain Policy"""
        return Policy(
            policy_id=UUID(db_model.policy_id),
            policy_number=db_model.policy_number,
            customer_id=UUID(db_model.customer_id),
            status=PolicyStatus(db_model.status),
            policy_type=db_model.policy_type,
            coverage_start=db_model.coverage_start,
            coverage_end=db_model.coverage_end,
            max_coverage_amount=db_model.max_coverage_amount,
        )
    
    def _to_db_model(self, policy: Policy) -> PolicyModel:
        """Convert domain Policy to database model"""
        return PolicyModel(
            policy_id=str(policy.policy_id),
            policy_number=policy.policy_number,
            customer_id=str(policy.customer_id),
            status=policy.status.value,
            policy_type=policy.policy_type,
            coverage_start=policy.coverage_start,
            coverage_end=policy.coverage_end,
            max_coverage_amount=policy.max_coverage_amount,
        )
    
    async def save(self, policy: Policy) -> None:
        """Save a policy to the database"""
        with get_db_session(self.db_path) as session:
            existing = session.query(PolicyModel).filter_by(
                policy_id=str(policy.policy_id)
            ).first()
            
            if existing:
                db_model = self._to_db_model(policy)
                for key, value in db_model.__dict__.items():
                    if key != "policy_id" and not key.startswith("_"):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                db_model = self._to_db_model(policy)
                session.add(db_model)
    
    async def find_by_id(self, policy_id: UUID) -> Optional[Policy]:
        """Find a policy by ID"""
        with get_db_session(self.db_path) as session:
            db_model = session.query(PolicyModel).filter_by(
                policy_id=str(policy_id)
            ).first()
            
            if db_model:
                return self._to_domain(db_model)
            return None
    
    async def find_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """Find a policy by policy number"""
        with get_db_session(self.db_path) as session:
            db_model = session.query(PolicyModel).filter_by(
                policy_number=policy_number
            ).first()
            
            if db_model:
                return self._to_domain(db_model)
            return None
    
    async def find_active_policies(self) -> List[Policy]:
        """Find all active policies"""
        with get_db_session(self.db_path) as session:
            db_models = session.query(PolicyModel).filter_by(
                status=PolicyStatus.ACTIVE.value
            ).all()
            return [self._to_domain(model) for model in db_models]

