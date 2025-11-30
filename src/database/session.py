"""
Database Session Management

Provides database session management and initialization.
"""

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Base, get_engine, get_session_factory


def init_db(db_path: str = "data/claims.db") -> None:
    """
    Initialize the database.
    
    Creates all tables if they don't exist.
    
    Args:
        db_path: Path to the database file
    """
    # Create data directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine and tables
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)


@contextmanager
def get_db_session(db_path: str = "data/claims.db"):
    """
    Get a database session context manager.
    
    Usage:
        with get_db_session() as session:
            # Use session
            pass
    
    Args:
        db_path: Path to the database file
    
    Yields:
        SQLAlchemy Session
    """
    session_factory = get_session_factory(db_path)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

