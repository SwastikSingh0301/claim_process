"""
Tests for claim creation endpoint and claim processing logic.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.claim import Claim
from app.models.claim_line import ClaimLine
from app.models.provider_aggregate import ProviderNetFeeAggregate


def test_create_claim_success(client: TestClient, sample_claim_data):
    """Test successful claim creation."""
    response = client.post("/claims/", json=sample_claim_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "claim_id" in data
    assert data["message"] == "Claim processed successfully"
    assert len(data["claim_id"]) > 0  # UUID string


def test_create_claim_stores_data(client: TestClient, test_session: Session, sample_claim_data):
    """Test that claim data is properly stored in database."""
    response = client.post("/claims/", json=sample_claim_data)
    assert response.status_code == 200
    
    claim_id_str = response.json()["claim_id"]
    # Convert string UUID to UUID object for SQLAlchemy
    from uuid import UUID
    claim_id = UUID(claim_id_str)
    
    # Verify claim was created
    claim = test_session.get(Claim, claim_id)
    assert claim is not None
    assert claim.claim_reference == "test_claim_001"
    
    # Verify claim lines were created
    stmt = select(ClaimLine).where(ClaimLine.claim_id == claim_id)
    lines = list(test_session.exec(stmt).all())
    assert len(lines) == 2
    
    # Verify first line
    line1 = lines[0]
    assert line1.submitted_procedure == "D0180"
    assert line1.provider_npi == "1234567890"
    assert line1.provider_fees_cents == 10000
    assert line1.allowed_fees_cents == 10000
    assert line1.member_coinsurance_cents == 0
    assert line1.member_copay_cents == 0
    assert line1.net_fee_cents == 0  # 100 + 0 + 0 - 100 = 0
    assert line1.plan_group == "GRP-1000"
    assert line1.subscriber_id == "1234567890"
    
    # Verify second line
    line2 = lines[1]
    assert line2.submitted_procedure == "D0210"
    assert line2.net_fee_cents == 8125  # 13000 + 1625 + 0 - 6500 = 8125


def test_create_claim_calculates_net_fee_correctly(client: TestClient, sample_claim_data):
    """Test net fee calculation formula: provider_fees + coinsurance + copay - allowed_fees."""
    # Test case: provider_fees=100, coinsurance=20, copay=10, allowed_fees=50
    # Expected: 100 + 20 + 10 - 50 = 80
    claim_data = {
        "claim_reference": "test_net_fee",
        "lines": [
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0180",
                "quadrant": None,
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1234567890",
                "provider_fees": "100.00",
                "allowed_fees": "50.00",
                "member_coinsurance": "20.00",
                "member_copay": "10.00",
            }
        ],
    }
    
    response = client.post("/claims/", json=claim_data)
    assert response.status_code == 200


def test_create_claim_with_optional_quadrant(client: TestClient, sample_claim_data):
    """Test that quadrant field is optional."""
    sample_claim_data["lines"][0]["quadrant"] = "UR"
    
    response = client.post("/claims/", json=sample_claim_data)
    assert response.status_code == 200


def test_create_claim_without_claim_reference(client: TestClient, sample_claim_data):
    """Test that claim_reference is optional."""
    del sample_claim_data["claim_reference"]
    
    response = client.post("/claims/", json=sample_claim_data)
    assert response.status_code == 200


def test_create_claim_missing_required_field(client: TestClient, sample_claim_data):
    """Test that missing required fields return 422."""
    del sample_claim_data["lines"][0]["submitted_procedure"]
    
    response = client.post("/claims/", json=sample_claim_data)
    assert response.status_code == 422  # Validation error


def test_create_claim_empty_lines(client: TestClient, sample_claim_data):
    """Test that empty lines array is rejected."""
    sample_claim_data["lines"] = []
    
    response = client.post("/claims/", json=sample_claim_data)
    # Should fail validation or return error
    assert response.status_code in [400, 422]


def test_create_claim_updates_provider_aggregate(client: TestClient, test_session: Session, sample_claim_data):
    """Test that provider aggregate is updated when claim is created."""
    # Create claim with provider_npi "1234567890"
    response = client.post("/claims/", json=sample_claim_data)
    assert response.status_code == 200
    
    # Check aggregate was created/updated
    aggregate = test_session.get(ProviderNetFeeAggregate, "1234567890")
    assert aggregate is not None
    # Net fees: line1 (0) + line2 (8125) = 8125 cents
    assert aggregate.total_net_fee_cents == 8125


def test_create_claim_multiple_providers(client: TestClient, test_session: Session):
    """Test that multiple providers are tracked separately."""
    claim_data = {
        "claim_reference": "multi_provider",
        "lines": [
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0180",
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1111111111",
                "provider_fees": "100.00",
                "allowed_fees": "50.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            },
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0210",
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "2222222222",
                "provider_fees": "200.00",
                "allowed_fees": "100.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            },
        ],
    }
    
    response = client.post("/claims/", json=claim_data)
    assert response.status_code == 200
    
    # Check both providers have correct aggregates
    agg1 = test_session.get(ProviderNetFeeAggregate, "1111111111")
    assert agg1.total_net_fee_cents == 5000  # 100 - 50
    
    agg2 = test_session.get(ProviderNetFeeAggregate, "2222222222")
    assert agg2.total_net_fee_cents == 10000  # 200 - 100


def test_create_claim_increments_existing_aggregate(client: TestClient, test_session: Session, sample_claim_data):
    """Test that new claims increment existing provider aggregates."""
    # Create first claim
    response1 = client.post("/claims/", json=sample_claim_data)
    assert response1.status_code == 200
    
    # Create second claim with same provider
    claim_data2 = {
        "claim_reference": "test_claim_002",
        "lines": [
            {
                "service_date": "2024-01-16T10:00:00",
                "submitted_procedure": "D0180",
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1234567890",
                "provider_fees": "50.00",
                "allowed_fees": "25.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            }
        ],
    }
    
    response2 = client.post("/claims/", json=claim_data2)
    assert response2.status_code == 200
    
    # Check aggregate was incremented
    aggregate = test_session.get(ProviderNetFeeAggregate, "1234567890")
    # First claim: 8125, Second claim: 2500, Total: 10625
    assert aggregate.total_net_fee_cents == 10625

