from fastapi.testclient import TestClient
from app.main import app

def test_read_presign():
    client = TestClient(app)
    response = client.get('/presign')
    assert response.status_code == 200
    assert response.json() == {"ok": true, "url": "demo"}
