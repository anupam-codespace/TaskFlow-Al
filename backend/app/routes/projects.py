"""
app/routes/projects.py — Project CRUD endpoints.

Route handlers are intentionally thin:
1. Validate input via schema.
2. Delegate to the service layer.
3. Serialise the result and return.

This keeps routes readable and pushes business logic where it belongs.
"""

from flask import Blueprint, jsonify, request, current_app
from marshmallow import ValidationError
from app.schemas import (
    project_create_schema, project_update_schema,
    project_response_schema, projects_response_schema,
)
from app.services import (
    get_all_projects, get_project_by_id,
    create_project, update_project, delete_project,
)
from app.services.task_service import get_stats_for_project

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("", methods=["GET"])
def list_projects():
    """GET /api/projects — List all projects."""
    projects = get_all_projects()
    return jsonify(projects_response_schema.dump(projects)), 200


@projects_bp.route("/<int:project_id>", methods=["GET"])
def get_project(project_id: int):
    """GET /api/projects/<id> — Get a single project with task stats."""
    project = get_project_by_id(project_id)
    if not project:
        return jsonify({"error": f"Project {project_id} not found."}), 404

    data = project_response_schema.dump(project)
    data["stats"] = get_stats_for_project(project_id)
    return jsonify(data), 200


@projects_bp.route("", methods=["POST"])
def create_project_route():
    """POST /api/projects — Create a new project."""
    try:
        payload = project_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed.", "details": err.messages}), 400

    try:
        project = create_project(payload)
        return jsonify(project_response_schema.dump(project)), 201
    except ValueError as err:
        return jsonify({"error": str(err)}), 409
    except Exception as exc:
        current_app.logger.error("Unexpected error creating project: %s", exc)
        return jsonify({"error": "Internal server error."}), 500


@projects_bp.route("/<int:project_id>", methods=["PATCH"])
def update_project_route(project_id: int):
    """PATCH /api/projects/<id> — Partially update a project."""
    project = get_project_by_id(project_id)
    if not project:
        return jsonify({"error": f"Project {project_id} not found."}), 404

    try:
        payload = project_update_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Validation failed.", "details": err.messages}), 400

    try:
        updated = update_project(project, payload)
        return jsonify(project_response_schema.dump(updated)), 200
    except Exception as exc:
        current_app.logger.error("Unexpected error updating project %s: %s", project_id, exc)
        return jsonify({"error": "Internal server error."}), 500


@projects_bp.route("/<int:project_id>", methods=["DELETE"])
def delete_project_route(project_id: int):
    """DELETE /api/projects/<id> — Delete a project and all its tasks."""
    project = get_project_by_id(project_id)
    if not project:
        return jsonify({"error": f"Project {project_id} not found."}), 404

    try:
        delete_project(project)
        return jsonify({"message": f"Project {project_id} deleted."}), 200
    except Exception as exc:
        current_app.logger.error("Unexpected error deleting project %s: %s", project_id, exc)
        return jsonify({"error": "Internal server error."}), 500
