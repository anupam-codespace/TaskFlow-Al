# app/models/__init__.py
# Re-export models so imports stay clean: `from app.models import Project, Task`
from app.models.project import Project
from app.models.task import Task

__all__ = ["Project", "Task"]
