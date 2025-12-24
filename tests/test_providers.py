"""
Tests for providers endpoint (top 10 by net fees).
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.provider_aggregate import ProviderNetFeeAggregate


def test_top_providers_empty(client: TestClient):
    """Test top providers endpoint with no data."""
    response = client.get("/providers/top")
    assert response.status_code == 200
    assert response.json() == []


def test_top_providers_single_provider(client: TestClient, test_session: Session):
    """Test top providers with single provider."""
    # Create aggregate directly
    aggregate = ProviderNetFeeAggregate(
        provider_npi="1111111111",
        total_net_fee_cents=100000,
    )
    test_session.add(aggregate)
    test_session.commit()
    
    response = client.get("/providers/top")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["provider_npi"] == "1111111111"
    assert data[0]["total_net_fee_cents"] == 100000


def test_top_providers_returns_top_10(client: TestClient, test_session: Session):
    """Test that endpoint returns exactly top 10 providers."""
    # Create 15 providers with different net fees
    for i in range(15):
        aggregate = ProviderNetFeeAggregate(
            provider_npi=f"{i:010d}",
            total_net_fee_cents=100000 - (i * 1000),  # Decreasing order
        )
        test_session.add(aggregate)
    test_session.commit()
    
    response = client.get("/providers/top")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 10  # Should return only top 10
    
    # Verify they're in descending order
    for i in range(len(data) - 1):
        assert data[i]["total_net_fee_cents"] >= data[i + 1]["total_net_fee_cents"]


def test_top_providers_ordering(client: TestClient, test_session: Session):
    """Test that providers are returned in descending order by net fees."""
    providers = [
        ("1111111111", 50000),
        ("2222222222", 100000),
        ("3333333333", 75000),
        ("4444444444", 25000),
        ("5555555555", 90000),
    ]
    
    for npi, net_fee in providers:
        aggregate = ProviderNetFeeAggregate(
            provider_npi=npi,
            total_net_fee_cents=net_fee,
        )
        test_session.add(aggregate)
    test_session.commit()
    
    response = client.get("/providers/top")
    assert response.status_code == 200
    
    data = response.json()
    # Should be ordered: 100000, 90000, 75000, 50000, 25000
    assert data[0]["total_net_fee_cents"] == 100000
    assert data[1]["total_net_fee_cents"] == 90000
    assert data[2]["total_net_fee_cents"] == 75000
    assert data[3]["total_net_fee_cents"] == 50000
    assert data[4]["total_net_fee_cents"] == 25000


def test_top_providers_response_format(client: TestClient, test_session: Session):
    """Test that response has correct format."""
    aggregate = ProviderNetFeeAggregate(
        provider_npi="1234567890",
        total_net_fee_cents=50000,
    )
    test_session.add(aggregate)
    test_session.commit()
    
    response = client.get("/providers/top")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    item = data[0]
    assert "provider_npi" in item
    assert "total_net_fee_cents" in item
    assert isinstance(item["provider_npi"], str)
    assert isinstance(item["total_net_fee_cents"], int)


def test_top_providers_less_than_10(client: TestClient, test_session: Session):
    """Test endpoint when there are fewer than 10 providers."""
    # Create only 3 providers
    for i in range(3):
        aggregate = ProviderNetFeeAggregate(
            provider_npi=f"{i:010d}",
            total_net_fee_cents=100000 - (i * 10000),
        )
        test_session.add(aggregate)
    test_session.commit()
    
    response = client.get("/providers/top")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3  # Should return all 3, not 10


def test_top_providers_integration_with_claims(client: TestClient, test_session: Session):
    """Test that top providers reflects data from claim processing."""
    # Create claims that will update aggregates
    claim_data1 = {
        "claim_reference": "claim_1",
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
            }
        ],
    }
    
    claim_data2 = {
        "claim_reference": "claim_2",
        "lines": [
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0180",
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "2222222222",
                "provider_fees": "200.00",
                "allowed_fees": "100.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            }
        ],
    }
    
    # Create claims
    response1 = client.post("/claims/", json=claim_data1)
    assert response1.status_code == 200
    
    response2 = client.post("/claims/", json=claim_data2)
    assert response2.status_code == 200
    
    # Check top providers
    response = client.get("/providers/top")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Provider 2 should be first (higher net fee: 200-100=100 vs 100-50=50)
    assert data[0]["provider_npi"] == "2222222222"
    assert data[0]["total_net_fee_cents"] == 10000
    assert data[1]["provider_npi"] == "1111111111"
    assert data[1]["total_net_fee_cents"] == 5000

