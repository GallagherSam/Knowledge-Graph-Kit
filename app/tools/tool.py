from functools import lru_cache
from contextlib import contextmanager

from app.database import SessionLocal
from app.vector_store import VectorStore

from app.tools.note import Notes
from app.tools.person import Persons
from app.tools.project import Projects
from app.tools.shared import Shared
from app.tools.task import Tasks

class Tools:
    def __init__(self, mcp_instance):
        self.notes = Notes(mcp_instance, self)
        self.persons = Persons(mcp_instance, self)
        self.projects = Projects(mcp_instance, self)
        self.shared = Shared(mcp_instance, self)
        self.tasks = Tasks(mcp_instance, self)
    
    @contextmanager
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @property
    @lru_cache
    def vector_store(self):
        return VectorStore()
