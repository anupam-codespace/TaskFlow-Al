"""
app/routes/ai.py — AI-powered endpoints.

Exposes two actions:
  POST /api/ai/summarise  — Generate a task summary
  POST /api/ai/prioritise — Suggest a priority level

These endpoints check if the task already has a cached ai_summary to avoid
redundant API calls. The heuristic fallback ensures they always return
a useful answer even without an OpenAI key.
"""

from flask import Blueprint, jsonify, request, current_app
from app.services import get_task_by_id, update_task
from app.services.ai_service import summarise_task, suggest_priority

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/summarise/<int:task_id>", methods=["POST"])
def ai_summarise(task_id: int):
    """
    POST /api/ai/summarise/<task_id>

    Generate and cache an AI summary for a task.
    Returns cached version if already generated.
    """
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": f"Task {task_id} not found."}), 404

    # Return cached summary if available
    if task.ai_summary:
        current_app.logger.info("Returning cached AI summary for task id=%s", task_id)
        return jsonify({"task_id": task_id, "summary": task.ai_summary, "cached": True}), 200

    try:
        summary = summarise_task(task.title, task.description or "")
        update_task(task, {"ai_summary": summary})
        return jsonify({"task_id": task_id, "summary": summary, "cached": False}), 200
    except Exception as exc:
        current_app.logger.error("AI summarise failed for task %s: %s", task_id, exc)
        return jsonify({"error": "AI summarisation failed."}), 500


@ai_bp.route("/prioritise/<int:task_id>", methods=["POST"])
def ai_prioritise(task_id: int):
    """
    POST /api/ai/prioritise/<task_id>

    Suggest an appropriate priority for a task based on its content.
    Does NOT automatically apply the suggestion — the user decides.
    """
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": f"Task {task_id} not found."}), 404

    try:
        suggested = suggest_priority(task.title, task.description or "")
        return jsonify({
            "task_id": task_id,
            "current_priority": task.priority,
            "suggested_priority": suggested,
            "should_update": suggested != task.priority,
        }), 200
    except Exception as exc:
        current_app.logger.error("AI prioritise failed for task %s: %s", task_id, exc)
        return jsonify({"error": "AI prioritisation failed."}), 500


@ai_bp.route("/bulk-summarise/<int:project_id>", methods=["POST"])
def ai_bulk_summarise(project_id: int):
    """
    POST /api/ai/bulk-summarise/<project_id>

    Summarise all tasks in a project that don't yet have a cached summary.
    Returns a count of how many were processed.
    """
    from app.services import get_tasks_for_project, get_project_by_id

    if not get_project_by_id(project_id):
        return jsonify({"error": f"Project {project_id} not found."}), 404

    tasks = get_tasks_for_project(project_id)
    processed = 0
    errors = 0

    for task in tasks:
        if task.ai_summary:
            continue
        try:
            summary = summarise_task(task.title, task.description or "")
            update_task(task, {"ai_summary": summary})
            processed += 1
        except Exception as exc:
            current_app.logger.warning("Bulk summarise failed for task %s: %s", task.id, exc)
            errors += 1

    return jsonify({
        "project_id": project_id,
        "processed": processed,
        "errors": errors,
        "total_tasks": len(tasks),
    }), 200
