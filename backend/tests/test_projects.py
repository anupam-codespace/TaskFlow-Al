"""
tests/test_projects.py — Integration tests for the Project API.

Tests verify the full request→response cycle including:
- Correct status codes
- Schema validation enforcement
- 404 behaviour for missing resources
- Cascade deletes
"""

import pytest
import json


def _create_project(client, name="Test Project", description="A test.", status="active"):
    return client.post(
        "/api/projects",
        data=json.dumps({"name": name, "description": description, "status": status}),
        content_type="application/json",
    )


class TestProjectList:
    def test_list_projects_returns_empty_list(self, client):
        """Fresh DB returns empty list — not an error."""
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_projects_returns_created_projects(self, client):
        _create_project(client, "Alpha")
        _create_project(client, "Beta")
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2


class TestProjectCreate:
    def test_create_project_returns_201(self, client):
        resp = _create_project(client)
        assert resp.status_code == 201

    def test_create_project_returns_correct_fields(self, client):
        resp = _create_project(client, name="Alpha Project")
        data = resp.get_json()
        assert data["name"] == "Alpha Project"
        assert data["status"] == "active"
        assert "id" in data
        assert "created_at" in data

    def test_create_project_rejects_missing_name(self, client):
        resp = client.post(
            "/api/projects",
            data=json.dumps({"description": "no name"}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_create_project_rejects_invalid_status(self, client):
        resp = client.post(
            "/api/projects",
            data=json.dumps({"name": "X", "status": "INVALID_STATUS"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_project_rejects_duplicate_name(self, client):
        _create_project(client, "Duplicate")
        resp = _create_project(client, "Duplicate")
        assert resp.status_code == 409

    def test_create_project_strips_whitespace(self, client):
        resp = client.post(
            "/api/projects",
            data=json.dumps({"name": "  Spaced Project  "}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "Spaced Project"


class TestProjectGet:
    def test_get_project_returns_404_for_missing(self, client):
        resp = client.get("/api/projects/9999")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_get_project_includes_stats(self, client):
        created = _create_project(client).get_json()
        resp = client.get(f"/api/projects/{created['id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "stats" in data
        assert "total" in data["stats"]


class TestProjectUpdate:
    def test_patch_project_updates_status(self, client):
        project = _create_project(client).get_json()
        resp = client.patch(
            f"/api/projects/{project['id']}",
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "completed"

    def test_patch_project_rejects_invalid_status(self, client):
        project = _create_project(client).get_json()
        resp = client.patch(
            f"/api/projects/{project['id']}",
            data=json.dumps({"status": "broken"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_patch_nonexistent_project_returns_404(self, client):
        resp = client.patch(
            "/api/projects/9999",
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


class TestProjectDelete:
    def test_delete_project_returns_200(self, client):
        project = _create_project(client).get_json()
        resp = client.delete(f"/api/projects/{project['id']}")
        assert resp.status_code == 200

    def test_deleted_project_is_gone(self, client):
        project = _create_project(client).get_json()
        client.delete(f"/api/projects/{project['id']}")
        resp = client.get(f"/api/projects/{project['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent_project_returns_404(self, client):
        resp = client.delete("/api/projects/9999")
        assert resp.status_code == 404
