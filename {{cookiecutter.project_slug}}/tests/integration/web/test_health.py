from fastapi.testclient import TestClient


class TestHealthAPI:
    def test_health(self, client: TestClient) -> None:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == "OK"
