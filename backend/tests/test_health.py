"""
tests/test_health.py — Health endpoint tests.
"""


class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_includes_database_status(self, client):
        data = resp = client.get("/api/health").get_json()
        assert "status" in data
        assert "database" in data
        assert "version" in data

    def test_health_database_connected(self, client):
        data = client.get("/api/health").get_json()
        assert data["database"] == "connected"
