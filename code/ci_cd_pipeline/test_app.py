import pytest
from fastapi.testclient import TestClient
from app import app
import os

client = TestClient(app)

# Unit Tests
def test_health_check_healthy():
    os.environ["DB_CONNECTED"] = "true"
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_health_check_degraded():
    os.environ["DB_CONNECTED"] = "false"
    response = client.get("/health")
    assert response.status_code == 503
    os.environ["DB_CONNECTED"] = "true"  # Reset

def test_payment_validation_negative_amount():
    payload = {"account_id": "ACC10029", "amount": -50.0, "currency": "USD"}
    response = client.post("/api/v1/process-payment", json=payload)
    assert response.status_code == 400
    assert "strictly positive" in response.json()["detail"]

# Integration Tests
def test_payment_end_to_end_success():
    payload = {"account_id": "ACC99882", "amount": 149.99, "currency": "USD"}
    response = client.post("/api/v1/process-payment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert "tx_ACC99882_14999" in data["transaction_id"]

