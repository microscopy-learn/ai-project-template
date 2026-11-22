from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_returns_answer_and_sources():
    response = client.post("/ask", json={"question": "What does lineage show?"})
    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert body["latency_ms"] >= 0


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
