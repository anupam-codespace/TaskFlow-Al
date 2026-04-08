"""
app/models/task.py — SQLAlchemy Task model.

Enforces all valid status and priority values at the DB layer,
preventing invalid states from ever being persisted.
"""

from datetime import datetime, timezone
from app import db


VALID_STATUSES = ("todo", "in_progress", "done", "cancelled")
VALID_PRIORITIES = ("low", "medium", "high", "critical")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(*VALID_STATUSES, name="task_status"),
        nullable=False,
        default="todo",
    )
    priority = db.Column(
        db.Enum(*VALID_PRIORITIES, name="task_priority"),
        nullable=False,
        default="medium",
    )
    ai_summary = db.Column(db.Text, nullable=True)  # Cached AI-generated summary

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Back-reference to project
    project = db.relationship("Project", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
