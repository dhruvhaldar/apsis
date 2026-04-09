import pytest
from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_payload_too_large():
    # Attempt to send a request with a Content-Length header exceeding the 2MB limit
    headers = {"content-length": str((2 * 1024 * 1024) + 1)}
    response = client.post("/api/lqr", headers=headers, json={"A": [[0]], "B": [[0]], "Q": [[0]], "R": [[0]]})
    assert response.status_code == 413
    assert response.json() == {"detail": "Payload too large"}

def test_invalid_content_length():
    # Attempt to send a request with an invalid Content-Length header format
    headers = {"content-length": "invalid_integer"}
    response = client.post("/api/lqr", headers=headers, json={"A": [[0]], "B": [[0]], "Q": [[0]], "R": [[0]]})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid Content-Length header"}

def test_valid_payload():
    # Attempt a valid request where Content-Length should be within limits
    # We don't provide the header explicitly as TestClient will add it correctly based on the json body
    payload = {
        "A": [[0, 1], [-1, -1]],
        "B": [[0], [1]],
        "Q": [[1, 0], [0, 1]],
        "R": [[1]]
    }
    response = client.post("/api/lqr", json=payload)
    assert response.status_code == 200

def test_chunked_encoding_rejected():
    # Attempt to bypass Content-Length limit using chunked transfer encoding
    def generate_chunked():
        yield b'{"A": [[0]], "B": [[0]], "Q": [[0]], "R": [[0]]}'

    response = client.post(
        "/api/lqr",
        content=generate_chunked(),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 411
    assert response.json() == {"detail": "Chunked encoding not supported"}

def test_chunked_encoding_bypass_mixed_case():
    response = client.post(
        "/api/lqr",
        content=b'{"A": [[0]], "B": [[0]], "Q": [[0]], "R": [[0]]}',
        headers={"Content-Type": "application/json", "Transfer-Encoding": "Chunked"}
    )
    assert response.status_code == 411
    assert response.json() == {"detail": "Chunked encoding not supported"}

def test_chunked_encoding_bypass_multiple_encodings():
    def generate_chunked():
        yield b'{"A": [[0]], "B": [[0]], "Q": [[0]], "R": [[0]]}'

    response = client.post(
        "/api/lqr",
        content=generate_chunked(),
        headers={"Content-Type": "application/json", "Transfer-Encoding": "gzip, chunked"}
    )
    assert response.status_code == 411
    assert response.json() == {"detail": "Chunked encoding not supported"}
