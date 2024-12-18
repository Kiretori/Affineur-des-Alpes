import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

MEM_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for each test."""
    # Setup the engine, sessionmaker, and tables
    engine = create_engine(MEM_DB_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for each test
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Clean up after the test