import pytest
from fastapi.testclient import TestClient
from api.index import app, rate_limit_store

client = TestClient(app)

def test_rate_limit_exceeded():
    # Clear the rate limit store to ensure a clean state
    rate_limit_store.clear()

    payload = {
        "A": [[0, 1], [-1, -1]],
        "B": [[0], [1]],
        "Q": [[1, 0], [0, 1]],
        "R": [[1]]
    }

    # Send 50 successful requests (RATE_LIMIT_MAX_REQUESTS = 50)
    for _ in range(50):
        response = client.post("/api/lqr", json=payload)
        assert response.status_code == 200

    # The 51st request should be rate limited
    response = client.post("/api/lqr", json=payload)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests. Please try again later."}

def test_rate_limit_not_applied_to_non_api():
    rate_limit_store.clear()

    # We can hit a non-API endpoint multiple times
    for _ in range(55):
        response = client.get("/non-existent")
        # Assuming there is no catch-all route, we expect a 404, not a 429
        assert response.status_code == 404

def test_rate_limit_x_forwarded_for():
    rate_limit_store.clear()

    payload = {
        "A": [[0, 1], [-1, -1]],
        "B": [[0], [1]],
        "Q": [[1, 0], [0, 1]],
        "R": [[1]]
    }

    # Send 50 successful requests from IP 1.2.3.4
    for _ in range(50):
        response = client.post("/api/lqr", json=payload, headers={"X-Forwarded-For": "1.2.3.4"})
        assert response.status_code == 200

    # The 51st request from IP 1.2.3.4 should be rate limited
    response = client.post("/api/lqr", json=payload, headers={"X-Forwarded-For": "1.2.3.4"})
    assert response.status_code == 429

    # But a request from IP 5.6.7.8 should pass
    response = client.post("/api/lqr", json=payload, headers={"X-Forwarded-For": "5.6.7.8"})
    assert response.status_code == 200
