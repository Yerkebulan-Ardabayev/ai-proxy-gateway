from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat():
    response = client.post("/api/chat", json={"prompt": "Hello test"})
    assert response.status_code == 200
    data = response.json()
    assert data["cached"] is False
    assert data["tokens_used"] > 0


def test_cache():
    client.post("/api/chat", json={"prompt": "Cache test unique"})
    response = client.post("/api/chat", json={"prompt": "Cache test unique"})
    assert response.json()["cached"] is True


def test_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert "total_requests" in response.json()


def test_history():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert "requests" in response.json()
