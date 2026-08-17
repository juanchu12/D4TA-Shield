from fastapi.testclient import TestClient

from shield_engine.api.app import app
from shield_engine.config import settings

client = TestClient(app)
HEADERS = {"X-Internal-Token": settings.internal_token}


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["service"] == "shield-engine"


def test_upload_requires_token():
    res = client.post("/contracts/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert res.status_code == 401
