# app/services/__init__.py
from app.services.project_service import (
    get_all_projects, get_project_by_id,
    create_project, update_project, delete_project,
)
from app.services.task_service import (
    get_tasks_for_project, get_task_by_id,
    create_task, update_task, delete_task, get_stats_for_project,
)
from app.services.ai_service import summarise_task, suggest_priority

__all__ = [
    "get_all_projects", "get_project_by_id", "create_project", "update_project", "delete_project",
    "get_tasks_for_project", "get_task_by_id", "create_task", "update_task", "delete_task", "get_stats_for_project",
    "summarise_task", "suggest_priority",
]
