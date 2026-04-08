"""
app/schemas/task_schema.py — Marshmallow schemas for Task.

These schemas are the single gate for all task data entering the system.
Invalid priority or status values are rejected before they reach the DB.
"""

from marshmallow import Schema, fields, validate, pre_load


VALID_STATUSES = ("todo", "in_progress", "done", "cancelled")
VALID_PRIORITIES = ("low", "medium", "high", "critical")


class TaskCreateSchema(Schema):
    """Schema for POST /api/tasks — new task creation."""

    project_id = fields.Int(
        required=True,
        error_messages={"required": "project_id is required."},
    )
    title = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200),
        error_messages={"required": "Task title is required."},
    )
    description = fields.Str(load_default="", validate=validate.Length(max=5000))
    status = fields.Str(
        load_default="todo",
        validate=validate.OneOf(VALID_STATUSES, error="Invalid status."),
    )
    priority = fields.Str(
        load_default="medium",
        validate=validate.OneOf(VALID_PRIORITIES, error="Invalid priority."),
    )

    @pre_load
    def strip_strings(self, data: dict, **kwargs) -> dict:
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


class TaskUpdateSchema(Schema):
    """Schema for PATCH /api/tasks/<id> — partial updates."""

    title = fields.Str(validate=validate.Length(min=2, max=200))
    description = fields.Str(validate=validate.Length(max=5000))
    status = fields.Str(validate=validate.OneOf(VALID_STATUSES))
    priority = fields.Str(validate=validate.OneOf(VALID_PRIORITIES))

    @pre_load
    def strip_strings(self, data: dict, **kwargs) -> dict:
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


class TaskResponseSchema(Schema):
    """Schema for serialising Task model instances to JSON."""

    id = fields.Int(dump_only=True)
    project_id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    status = fields.Str()
    priority = fields.Str()
    ai_summary = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# Singleton instances
task_create_schema = TaskCreateSchema()
task_update_schema = TaskUpdateSchema()
task_response_schema = TaskResponseSchema()
tasks_response_schema = TaskResponseSchema(many=True)
