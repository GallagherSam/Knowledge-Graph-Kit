import datetime
import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field

# A union of all possible node types for type hinting
AnyNode = Literal["Task", "Note", "Person", "Project"]


class Node(BaseModel):
    """Base model for all nodes in the graph."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AnyNode
    properties: dict[str, Any]


class TaskProperties(BaseModel):
    """Properties specific to a Task node."""

    description: str
    status: Literal["todo", "in_progress", "in_review", "cancelled", "done"] = "todo"
    tags: list[str] = []
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    modified_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    due_date: datetime.datetime | None = None


class NoteProperties(BaseModel):
    """Properties specific to a Note node."""

    title: str
    content: str
    tags: list[str] = []
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    modified_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class PersonProperties(BaseModel):
    """Properties specific to a Person node."""

    name: str
    tags: list[str] = []
    metadata: dict[str, Any] = {}
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    modified_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class ProjectProperties(BaseModel):
    """Properties specific to a Project node."""

    name: str
    description: str
    tags: list[str] = []
    status: Literal["active", "archived"] = "active"
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    modified_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class Edge(BaseModel):
    """Model for an edge connecting two nodes."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    label: str
