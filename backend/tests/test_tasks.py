"""
tests/test_tasks.py — Integration tests for the Task API.

Verifies:
- Task creation with valid/invalid data
- Status and priority enum enforcement
- Task scoping to projects
- AI summarisation (heuristic path — no API key in tests)
"""

import json
import pytest


def _create_project(client, name="Test Project"):
    resp = client.post(
        "/api/projects",
        data=json.dumps({"name": name, "description": "Test"}),
        content_type="application/json",
    )
    return resp.get_json()


def _create_task(client, project_id, title="Fix bug", priority="medium", status="todo"):
    return client.post(
        "/api/tasks",
        data=json.dumps({
            "project_id": project_id,
            "title": title,
            "description": "A test task description.",
            "priority": priority,
            "status": status,
        }),
        content_type="application/json",
    )


class TestTaskCreate:
    def test_create_task_returns_201(self, client):
        project = _create_project(client)
        resp = _create_task(client, project["id"])
        assert resp.status_code == 201

    def test_create_task_returns_correct_fields(self, client):
        project = _create_project(client)
        resp = _create_task(client, project["id"], title="Implement login", priority="high")
        data = resp.get_json()
        assert data["title"] == "Implement login"
        assert data["priority"] == "high"
        assert data["status"] == "todo"
        assert data["project_id"] == project["id"]

    def test_create_task_rejects_missing_title(self, client):
        project = _create_project(client)
        resp = client.post(
            "/api/tasks",
            data=json.dumps({"project_id": project["id"]}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_task_rejects_invalid_priority(self, client):
        project = _create_project(client)
        resp = client.post(
            "/api/tasks",
            data=json.dumps({
                "project_id": project["id"],
                "title": "Bad priority",
                "priority": "SUPER_URGENT",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_task_rejects_invalid_status(self, client):
        project = _create_project(client)
        resp = client.post(
            "/api/tasks",
            data=json.dumps({
                "project_id": project["id"],
                "title": "Bad status",
                "status": "WONTFIX",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_task_for_nonexistent_project_returns_404(self, client):
        resp = _create_task(client, project_id=9999)
        assert resp.status_code == 404

    def test_create_task_strips_whitespace_in_title(self, client):
        project = _create_project(client)
        resp = client.post(
            "/api/tasks",
            data=json.dumps({"project_id": project["id"], "title": "  Padded Title  "}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.get_json()["title"] == "Padded Title"


class TestTaskList:
    def test_list_tasks_for_project_returns_empty(self, client):
        project = _create_project(client)
        resp = client.get(f"/api/tasks/project/{project['id']}")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_tasks_for_project_returns_created_tasks(self, client):
        project = _create_project(client)
        _create_task(client, project["id"], "Task A")
        _create_task(client, project["id"], "Task B")
        resp = client.get(f"/api/tasks/project/{project['id']}")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_list_tasks_for_nonexistent_project(self, client):
        resp = client.get("/api/tasks/project/9999")
        assert resp.status_code == 404


class TestTaskUpdate:
    def test_patch_task_updates_status(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"]).get_json()
        resp = client.patch(
            f"/api/tasks/{task['id']}",
            data=json.dumps({"status": "done"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "done"

    def test_patch_task_rejects_invalid_status(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"]).get_json()
        resp = client.patch(
            f"/api/tasks/{task['id']}",
            data=json.dumps({"status": "invalid"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_patch_nonexistent_task_returns_404(self, client):
        resp = client.patch(
            "/api/tasks/9999",
            data=json.dumps({"status": "done"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


class TestTaskDelete:
    def test_delete_task_returns_200(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"]).get_json()
        resp = client.delete(f"/api/tasks/{task['id']}")
        assert resp.status_code == 200

    def test_deleted_task_is_gone(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"]).get_json()
        client.delete(f"/api/tasks/{task['id']}")
        resp = client.get(f"/api/tasks/{task['id']}")
        assert resp.status_code == 404


class TestAISummarise:
    def test_summarise_returns_200(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"], title="Fix production outage").get_json()
        resp = client.post(f"/api/ai/summarise/{task['id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "summary" in data
        assert len(data["summary"]) > 0

    def test_summarise_is_cached_on_second_call(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"], title="Refactor auth module").get_json()

        resp1 = client.post(f"/api/ai/summarise/{task['id']}")
        resp2 = client.post(f"/api/ai/summarise/{task['id']}")

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp2.get_json()["cached"] is True

    def test_prioritise_returns_valid_priority(self, client):
        project = _create_project(client)
        task = _create_task(client, project["id"], title="Production security breach fix").get_json()
        resp = client.post(f"/api/ai/prioritise/{task['id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["suggested_priority"] in ("low", "medium", "high", "critical")
