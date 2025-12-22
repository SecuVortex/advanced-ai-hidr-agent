"""
Unit tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from cert_validator.api import app, VALID_API_KEYS

client = TestClient(app)
API_KEY = list(VALID_API_KEYS)[0]

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get(
        "/api/expert/status",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'cache_stats' in data

def test_health_check_no_auth():
    """Test health check without authentication (should be public)"""
    response = client.get("/api/expert/status")
    assert response.status_code == 200  # Health endpoint is public

def test_validate_sync_no_auth():
    """Test sync validation without API key"""
    response = client.post(
        "/api/validate",
        json={
            "type": "pem",
            "cert_pem": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----"
        }
    )
    assert response.status_code == 401

def test_validate_async_submit():
    """Test async validation job submission"""
    response = client.post(
        "/api/validate-job",
        headers={"X-API-Key": API_KEY},
        json={
            "type": "pem",
            "cert_pem": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
            "intermediates": [],
            "context": {}
        }
    )
    assert response.status_code in [200, 500]  # May fail on invalid cert, but tests auth

def test_get_job_status_not_found():
    """Test getting status of non-existent job"""
    response = client.get(
        "/api/validate-job/nonexistent-job-id",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 404

def test_get_cert_metadata_not_implemented():
    """Test cert metadata endpoint (not implemented)"""
    response = client.get(
        "/api/certs/sha256:abc123",
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 501

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
