
import logging
from typing import Optional
from app import db
from app.models.task import Task

logger = logging.getLogger(__name__)


def get_tasks_for_project(project_id: int) -> list[Task]:
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    tasks = Task.query.filter_by(project_id=project_id).all()
    return sorted(tasks, key=lambda t: (priority_order.get(t.priority, 99), t.created_at))


def get_task_by_id(task_id: int) -> Optional[Task]:
    from app import db
    return db.session.get(Task, task_id)


def create_task(data: dict) -> Task:
    """
    Persist a new task.

    Args:
        data: Validated dictionary from TaskCreateSchema.

    Returns:
        The newly created Task instance.
    """
    task = Task(
        project_id=data["project_id"],
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "todo"),
        priority=data.get("priority", "medium"),
    )
    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Created task id=%s title=%r project_id=%s", task.id, task.title, task.project_id)
        return task
    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to create task: %s", exc)
        raise


def update_task(task: Task, data: dict) -> Task:
    """
    Apply partial updates to an existing task.

    Args:
        task: The Task instance to update.
        data: Validated dictionary from TaskUpdateSchema.

    Returns:
        The updated Task instance.
    """
    for field in ("title", "description", "status", "priority", "ai_summary"):
        if field in data:
            setattr(task, field, data[field])
    try:
        db.session.commit()
        logger.info("Updated task id=%s", task.id)
        return task
    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to update task id=%s: %s", task.id, exc)
        raise


def delete_task(task: Task) -> None:
    """
    Delete a task.

    Args:
        task: The Task instance to delete.
    """
    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Deleted task id=%s", task.id)
    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to delete task id=%s: %s", task.id, exc)
        raise


def get_stats_for_project(project_id: int) -> dict:
    """Return aggregated task statistics for a project."""
    tasks = Task.query.filter_by(project_id=project_id).all()
    stats = {"total": len(tasks), "todo": 0, "in_progress": 0, "done": 0, "cancelled": 0}
    for t in tasks:
        stats[t.status] = stats.get(t.status, 0) + 1
    completion = (stats["done"] / stats["total"] * 100) if stats["total"] else 0
    stats["completion_pct"] = round(completion, 1)
    return stats
