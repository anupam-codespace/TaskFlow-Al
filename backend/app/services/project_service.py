"""
app/services/project_service.py — Business logic for Projects.

Routes delegate to this service. The service owns all DB interactions
and business rules. This separation means:
- Routes stay thin and readable.
- Business rules are tested without HTTP overhead.
- Swapping the DB layer only touches this file.
"""

import logging
from typing import Optional
from app import db
from app.models.project import Project

logger = logging.getLogger(__name__)


def get_all_projects() -> list[Project]:
    """Return all projects ordered by creation date (newest first)."""
    return Project.query.order_by(Project.created_at.desc()).all()


def get_project_by_id(project_id: int) -> Optional[Project]:
    """Return a project by ID, or None if not found."""
    from app import db
    return db.session.get(Project, project_id)


def create_project(data: dict) -> Project:
    """
    Persist a new project.

    Args:
        data: Validated dictionary from ProjectCreateSchema.

    Returns:
        The newly created Project instance.

    Raises:
        ValueError: If a project with the same name already exists.
    """
    if Project.query.filter_by(name=data["name"]).first():
        raise ValueError(f"A project named '{data['name']}' already exists.")

    project = Project(
        name=data["name"],
        description=data.get("description", ""),
        status=data.get("status", "active"),
    )
    try:
        db.session.add(project)
        db.session.commit()
        logger.info("Created project id=%s name=%r", project.id, project.name)
        return project
    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to create project: %s", exc)
        raise


def update_project(project: Project, data: dict) -> Project:
    """
    Apply partial updates to an existing project.

    Args:
        project: The Project instance to update.
        data: Validated dictionary from ProjectUpdateSchema.

    Returns:
        The updated Project instance.
    """
    for field in ("name", "description", "status"):
        if field in data:
            setattr(project, field, data[field])
    try:
        db.session.commit()
        logger.info("Updated project id=%s", project.id)
        return project
    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to update project id=%s: %s", project.id, exc)
        raise


def delete_project(project: Project) -> None:
    """
    Delete a project and all its tasks (handled by cascade).

    Args:
        project: The Project instance to delete.
    """
    try:
        db.session.delete(project)
        db.session.commit()
        logger.info("Deleted project id=%s", project.id)
    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to delete project id=%s: %s", project.id, exc)
        raise
