# app/schemas/__init__.py
from app.schemas.project_schema import (
    project_create_schema,
    project_update_schema,
    project_response_schema,
    projects_response_schema,
)
from app.schemas.task_schema import (
    task_create_schema,
    task_update_schema,
    task_response_schema,
    tasks_response_schema,
)

__all__ = [
    "project_create_schema", "project_update_schema",
    "project_response_schema", "projects_response_schema",
    "task_create_schema", "task_update_schema",
    "task_response_schema", "tasks_response_schema",
]
