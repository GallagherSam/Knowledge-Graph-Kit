from contextlib import contextmanager

from app.config import AppConfig
from app.database import init_db
from app.tools.note import Notes
from app.tools.person import Persons
from app.tools.project import Projects
from app.tools.shared import Shared
from app.tools.task import Tasks
from app.vector_store import VectorStore


class Tools:
    def __init__(self, mcp_instance, config: AppConfig):
        """
        Initialize tools with configuration.

        Args:
            mcp_instance: The FastMCP instance
            config: Application configuration
        """
        self.config = config
        self._session_local = None
        self._vector_store = None

        # Initialize tools
        self.notes = Notes(mcp_instance, self)
        self.persons = Persons(mcp_instance, self)
        self.projects = Projects(mcp_instance, self)
        self.shared = Shared(mcp_instance, self)
        self.tasks = Tasks(mcp_instance, self)

    @contextmanager
    def get_db(self):
        if self._session_local is None:
            self._session_local = init_db(self.config.SQLALCHEMY_DATABASE_URL)

        db = self._session_local()
        try:
            yield db
        finally:
            db.close()

    @property
    def vector_store(self):
        """Lazy-load vector store singleton."""
        if self._vector_store is None:
            self._vector_store = VectorStore(
                chroma_data_path=self.config.CHROMA_DATA_PATH,
                embedding_model=self.config.EMBEDDING_MODEL
            )
        return self._vector_store
