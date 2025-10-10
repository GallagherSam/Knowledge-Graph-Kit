import datetime
import uuid
from typing import Literal, Optional, Dict, Any, List

from pydantic import BaseModel, Field

# A union of all possible node types for type hinting
AnyNode = Literal["Task", "Note", "Person", "Project"]

class Node(BaseModel):
    """Base model for all nodes in the graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AnyNode
    properties: Dict[str, Any]

class TaskProperties(BaseModel):
    """Properties specific to a Task node."""
    description: str
    status: Literal['todo', 'in_progress', 'in_review', 'cancelled', 'done'] = 'todo'
    tags: List[str] = []
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    due_date: Optional[datetime.datetime] = None

class NoteProperties(BaseModel):
    """Properties specific to a Note node."""
    title: str
    content: str
    tags: List[str] = []
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    modified_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class PersonProperties(BaseModel):
    """Properties specific to a Person node."""
    name: str
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ProjectProperties(BaseModel):
    """Properties specific to a Project node."""
    name: str
    description: str
    tags: List[str] = []
    status: Literal['active', 'archived'] = 'active'

class Edge(BaseModel):
    """Model for an edge connecting two nodes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    label: str
