"""
app/routes/tasks.py — Task CRUD endpoints.

Tasks are scoped to projects. You can also list all tasks globally
(useful for dashboard views). Every mutation validates with a schema
before touching the service layer.
"""

from flask import Blueprint, jsonify, request, current_app
from marshmallow import ValidationError
from app.schemas import (
    task_create_schema, task_update_schema,
    task_response_schema, tasks_response_schema,
)
from app.services import (
    get_tasks_for_project, get_task_by_id,
    create_task, update_task, delete_task,
    get_project_by_id,
)
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/project/<int:project_id>", methods=["GET"])
def list_tasks_for_project(project_id: int):
    """GET /api/tasks/project/<project_id> — List tasks for a project."""
    if not get_project_by_id(project_id):
        return jsonify({"error": f"Project {project_id} not found."}), 404

    tasks = get_tasks_for_project(project_id)
    return jsonify(tasks_response_schema.dump(tasks)), 200


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    """GET /api/tasks/<id> — Get a single task."""
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": f"Task {task_id} not found."}), 404
    return jsonify(task_response_schema.dump(task)), 200


@tasks_bp.route("", methods=["POST"])
def create_task_route():
    """POST /api/tasks — Create a new task."""
    try:
        payload = task_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed.", "details": err.messages}), 400

    if not get_project_by_id(payload["project_id"]):
        return jsonify({"error": f"Project {payload['project_id']} not found."}), 404

    try:
        task = create_task(payload)
        return jsonify(task_response_schema.dump(task)), 201
    except Exception as exc:
        current_app.logger.error("Unexpected error creating task: %s", exc)
        return jsonify({"error": "Internal server error."}), 500


@tasks_bp.route("/<int:task_id>", methods=["PATCH"])
def update_task_route(task_id: int):
    """PATCH /api/tasks/<id> — Partially update a task."""
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": f"Task {task_id} not found."}), 404

    try:
        payload = task_update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed.", "details": err.messages}), 400

    try:
        updated = update_task(task, payload)
        return jsonify(task_response_schema.dump(updated)), 200
    except Exception as exc:
        current_app.logger.error("Unexpected error updating task %s: %s", task_id, exc)
        return jsonify({"error": "Internal server error."}), 500


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task_route(task_id: int):
    """DELETE /api/tasks/<id> — Delete a task."""
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": f"Task {task_id} not found."}), 404

    try:
        delete_task(task)
        return jsonify({"message": f"Task {task_id} deleted."}), 200
    except Exception as exc:
        current_app.logger.error("Unexpected error deleting task %s: %s", task_id, exc)
        return jsonify({"error": "Internal server error."}), 500
