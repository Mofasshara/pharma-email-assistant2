from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_banking_health():
    r = client.get("/banking/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
