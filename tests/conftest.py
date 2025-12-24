"""
Pytest configuration and fixtures for testing.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_session
from app.models.claim import Claim
from app.models.claim_line import ClaimLine
from app.models.provider_aggregate import ProviderNetFeeAggregate


# Use file-based SQLite for testing (in-memory doesn't work with multiple connections)
import tempfile
import os
_test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
_test_db_file.close()
TEST_DATABASE_URL = f"sqlite:///{_test_db_file.name}"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    # Create a unique database file for each test
    import tempfile
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_file.close()
    db_url = f"sqlite:///{db_file.name}"
    
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    # Create all tables - models are already imported at module level
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()
    # Clean up the temp file
    try:
        os.unlink(db_file.name)
    except:
        pass


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session
        session.rollback()


@pytest.fixture(scope="function")
def client(test_engine):
    """Create a test client with overridden database session."""
    # Ensure tables are created
    SQLModel.metadata.create_all(test_engine)
    
    def override_get_session():
        with Session(test_engine) as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_claim_data():
    """Sample claim data for testing."""
    return {
        "claim_reference": "test_claim_001",
        "lines": [
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0180",
                "quadrant": None,
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1234567890",
                "provider_fees": "100.00",
                "allowed_fees": "100.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            },
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0210",
                "quadrant": None,
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1234567890",
                "provider_fees": "130.00",
                "allowed_fees": "65.00",
                "member_coinsurance": "16.25",
                "member_copay": "0.00",
            },
        ],
    }

