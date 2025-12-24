"""
Tests for rate limiting functionality.
"""
import pytest
from fastapi.testclient import TestClient
from time import sleep
from app.core.rate_limiter import limiter


@pytest.fixture(autouse=True)
def reset_limiter_before_test():
    """Reset rate limiter before each test."""
    # Reset the limiter's storage between tests
    limiter.reset()
    yield
    limiter.reset()


def test_rate_limiting_allows_requests(client: TestClient):
    """Test that rate limiting allows requests within limit."""
    # Make a few requests (should be fine)
    for i in range(5):
        response = client.get("/providers/top")
        assert response.status_code == 200, f"Request {i+1} should succeed"


def test_rate_limiting_blocks_excessive_requests(client: TestClient):
    """Test that rate limiting blocks requests exceeding 10/minute."""
    # Make 11 requests rapidly
    responses = []
    for i in range(11):
        response = client.get("/providers/top")
        responses.append(response)
    
    # First 10 should succeed, 11th should be rate limited
    status_codes = [r.status_code for r in responses]
    assert status_codes[:10] == [200] * 10, "First 10 requests should succeed"
    assert status_codes[10] == 429, "11th request should be rate limited"


def test_rate_limiting_only_on_providers_endpoint(client: TestClient, sample_claim_data):
    """Test that rate limiting only applies to /providers/top, not other endpoints."""
    # Health endpoint should not be rate limited
    for i in range(20):
        response = client.get("/health")
        assert response.status_code == 200, f"Health check {i+1} should not be rate limited"
    
    # Claims endpoint should not be rate limited
    for i in range(5):
        response = client.post("/claims/", json=sample_claim_data)
        assert response.status_code == 200, f"Claim creation {i+1} should not be rate limited"


def test_rate_limiting_error_message(client: TestClient):
    """Test that rate limited requests return appropriate error message."""
    # Try to exceed rate limit
    responses = []
    for i in range(15):
        response = client.get("/providers/top")
        responses.append(response)
        if response.status_code == 429:
            # If we hit rate limit, check error message
            assert "rate limit" in response.json()["detail"].lower()
            break

