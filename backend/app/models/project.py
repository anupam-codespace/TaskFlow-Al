"""
app/models/project.py — SQLAlchemy Project model.

Single source of truth for the projects table. Any schema change
(adding a column) happens here and propagates everywhere automatically.
"""

from datetime import datetime, timezone
from app import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum("active", "completed", "archived", name="project_status"),
        nullable=False,
        default="active",
    )
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

    # Relationship — tasks cascade-delete when project is deleted
    tasks = db.relationship(
        "Task", back_populates="project", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} status={self.status}>"
