"""
app/__init__.py — Application factory.

Using the factory pattern means:
- Tests can spin up isolated app instances with their own DB.
- Configuration is injected, not hard-coded.
- Blueprints are registered in one place; adding a new module is a 2-line change.
"""

import logging
import sys
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config_map, Config

# Single shared SQLAlchemy instance; bound to the app in create_app()
db = SQLAlchemy()


def create_app(config_name: str = "development") -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_name: One of 'development', 'testing', 'production'.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # ── Configuration ─────────────────────────────────────────────────────────
    cfg = config_map.get(config_name, Config)
    app.config.from_object(cfg)

    # ── Logging ───────────────────────────────────────────────────────────────
    _setup_logging(app)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.tasks import tasks_bp
    from app.routes.projects import projects_bp
    from app.routes.ai import ai_bp
    from app.routes.health import health_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    # ── Database initialisation ───────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_if_empty()

    app.logger.info("TaskFlow API started in '%s' mode", config_name)
    return app


def _setup_logging(app: Flask) -> None:
    """Configure structured logging to stdout."""
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(level)


def _seed_if_empty() -> None:
    """Seed the database with demo data on first run."""
    from app.models.project import Project
    from app.models.task import Task

    if Project.query.count() > 0:
        return

    projects = [
        Project(
            name="TaskFlow Platform",
            description="Build the core task management platform with AI assistance.",
            status="active",
        ),
        Project(
            name="Mobile SDK",
            description="React Native SDK for the TaskFlow mobile experience.",
            status="active",
        ),
        Project(
            name="Analytics Dashboard",
            description="Real-time analytics and reporting for project metrics.",
            status="completed",
        ),
    ]
    db.session.add_all(projects)
    db.session.flush()

    tasks = [
        Task(project_id=projects[0].id, title="Design REST API schema", description="Define all endpoints, request/response shapes, and error codes.", priority="high", status="done"),
        Task(project_id=projects[0].id, title="Implement authentication middleware", description="JWT-based auth guard for protected routes.", priority="high", status="in_progress"),
        Task(project_id=projects[0].id, title="Write integration tests", description="Cover all critical paths with pytest.", priority="medium", status="todo"),
        Task(project_id=projects[0].id, title="Set up structured logging", description="Add request-scoped log context with correlation IDs.", priority="low", status="todo"),
        Task(project_id=projects[1].id, title="Initialize React Native project", description="Bootstrap with Expo and configure ESLint/Prettier.", priority="high", status="done"),
        Task(project_id=projects[1].id, title="Build task list component", description="Virtualized list supporting swipe gestures.", priority="medium", status="in_progress"),
        Task(project_id=projects[1].id, title="Offline sync strategy", description="Design and implement local SQLite + sync queue for offline-first support.", priority="high", status="todo"),
        Task(project_id=projects[2].id, title="Design metrics schema", description="Define KPIs and aggregation windows.", priority="medium", status="done"),
        Task(project_id=projects[2].id, title="Build chart components", description="Recharts-based responsive chart library.", priority="medium", status="done"),
    ]
    db.session.add_all(tasks)
    db.session.commit()
