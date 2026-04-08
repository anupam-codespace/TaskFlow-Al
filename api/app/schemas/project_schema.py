"""
app/schemas/project_schema.py — Marshmallow schemas for Project.

Schemas serve as the contract between the HTTP layer and the service layer.
They validate inbound data and serialise outbound data, ensuring the API
surface is never touched by raw, unchecked request payloads.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


VALID_STATUSES = ("active", "completed", "archived")


class ProjectCreateSchema(Schema):
    """Schema for POST /api/projects — new project creation."""

    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=120),
        error_messages={"required": "Project name is required."},
    )
    description = fields.Str(load_default="", validate=validate.Length(max=2000))
    status = fields.Str(
        load_default="active",
        validate=validate.OneOf(VALID_STATUSES, error="Invalid status value."),
    )

    @pre_load
    def strip_strings(self, data: dict, **kwargs) -> dict:
        """Strip leading/trailing whitespace from all string fields."""
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


class ProjectUpdateSchema(Schema):
    """Schema for PATCH /api/projects/<id> — partial updates."""

    name = fields.Str(validate=validate.Length(min=2, max=120))
    description = fields.Str(validate=validate.Length(max=2000))
    status = fields.Str(validate=validate.OneOf(VALID_STATUSES))

    @pre_load
    def strip_strings(self, data: dict, **kwargs) -> dict:
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


class ProjectResponseSchema(Schema):
    """Schema for serialising Project model instances to JSON."""

    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    status = fields.Str()
    task_count = fields.Method("get_task_count")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def get_task_count(self, obj) -> int:
        return obj.tasks.count() if hasattr(obj, "tasks") else 0


# Singleton instances — reuse across requests to avoid re-construction overhead
project_create_schema = ProjectCreateSchema()
project_update_schema = ProjectUpdateSchema()
project_response_schema = ProjectResponseSchema()
projects_response_schema = ProjectResponseSchema(many=True)
