"""
Tests for data validation rules.
"""
import pytest
from fastapi.testclient import TestClient


def test_validation_submitted_procedure_must_start_with_d(client: TestClient):
    """Test that submitted_procedure must start with 'D'."""
    claim_data = {
        "claim_reference": "test_validation",
        "lines": [
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "C1234",  # Invalid: starts with C
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1234567890",
                "provider_fees": "100.00",
                "allowed_fees": "100.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            }
        ],
    }
    
    response = client.post("/claims/", json=claim_data)
    assert response.status_code == 400
    assert "submitted_procedure must start with 'D'" in response.json()["detail"]


def test_validation_submitted_procedure_valid(client: TestClient):
    """Test that valid submitted_procedure values are accepted."""
    valid_procedures = ["D0180", "D0210", "D4346", "D4211", "D1234"]
    
    for procedure in valid_procedures:
        claim_data = {
            "claim_reference": "test_validation",
            "lines": [
                {
                    "service_date": "2024-01-15T10:00:00",
                    "submitted_procedure": procedure,
                    "plan_group": "GRP-1000",
                    "subscriber_id": "1234567890",
                    "provider_npi": "1234567890",
                    "provider_fees": "100.00",
                    "allowed_fees": "100.00",
                    "member_coinsurance": "0.00",
                    "member_copay": "0.00",
                }
            ],
        }
        
        response = client.post("/claims/", json=claim_data)
        assert response.status_code == 200, f"Procedure {procedure} should be valid"


def test_validation_provider_npi_must_be_10_digits(client: TestClient):
    """Test that provider_npi must be exactly 10 digits."""
    invalid_npis = [
        "123456789",      # 9 digits
        "12345678901",    # 11 digits
        "123456789a",     # contains letter
        "12345-6789",     # contains dash
        "",               # empty
    ]
    
    for npi in invalid_npis:
        claim_data = {
            "claim_reference": "test_validation",
            "lines": [
                {
                    "service_date": "2024-01-15T10:00:00",
                    "submitted_procedure": "D0180",
                    "plan_group": "GRP-1000",
                    "subscriber_id": "1234567890",
                    "provider_npi": npi,
                    "provider_fees": "100.00",
                    "allowed_fees": "100.00",
                    "member_coinsurance": "0.00",
                    "member_copay": "0.00",
                }
            ],
        }
        
        response = client.post("/claims/", json=claim_data)
        assert response.status_code == 400, f"NPI {npi} should be invalid"
        assert "provider_npi" in response.json()["detail"].lower()


def test_validation_provider_npi_valid(client: TestClient):
    """Test that valid 10-digit NPI values are accepted."""
    valid_npis = ["1234567890", "0000000000", "9999999999", "1497775530"]
    
    for npi in valid_npis:
        claim_data = {
            "claim_reference": "test_validation",
            "lines": [
                {
                    "service_date": "2024-01-15T10:00:00",
                    "submitted_procedure": "D0180",
                    "plan_group": "GRP-1000",
                    "subscriber_id": "1234567890",
                    "provider_npi": npi,
                    "provider_fees": "100.00",
                    "allowed_fees": "100.00",
                    "member_coinsurance": "0.00",
                    "member_copay": "0.00",
                }
            ],
        }
        
        response = client.post("/claims/", json=claim_data)
        assert response.status_code == 200, f"NPI {npi} should be valid"


def test_validation_required_fields(client: TestClient):
    """Test that all required fields (except quadrant) are validated."""
    required_fields = [
        "service_date",
        "submitted_procedure",
        "plan_group",
        "subscriber_id",
        "provider_npi",
        "provider_fees",
        "allowed_fees",
        "member_coinsurance",
        "member_copay",
    ]
    
    for field in required_fields:
        claim_data = {
            "claim_reference": "test_validation",
            "lines": [
                {
                    "service_date": "2024-01-15T10:00:00",
                    "submitted_procedure": "D0180",
                    "plan_group": "GRP-1000",
                    "subscriber_id": "1234567890",
                    "provider_npi": "1234567890",
                    "provider_fees": "100.00",
                    "allowed_fees": "100.00",
                    "member_coinsurance": "0.00",
                    "member_copay": "0.00",
                }
            ],
        }
        
        # Remove the required field
        del claim_data["lines"][0][field]
        
        response = client.post("/claims/", json=claim_data)
        assert response.status_code == 422, f"Field {field} should be required"


def test_validation_quadrant_is_optional(client: TestClient):
    """Test that quadrant field is optional."""
    claim_data = {
        "claim_reference": "test_validation",
        "lines": [
            {
                "service_date": "2024-01-15T10:00:00",
                "submitted_procedure": "D0180",
                # quadrant not included
                "plan_group": "GRP-1000",
                "subscriber_id": "1234567890",
                "provider_npi": "1234567890",
                "provider_fees": "100.00",
                "allowed_fees": "100.00",
                "member_coinsurance": "0.00",
                "member_copay": "0.00",
            }
        ],
    }
    
    response = client.post("/claims/", json=claim_data)
    assert response.status_code == 200

