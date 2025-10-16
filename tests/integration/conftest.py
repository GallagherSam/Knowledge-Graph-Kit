
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, PropertyMock
import chromadb
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.tools.tool import Tools
from app.database import Base
from app.vector_store import VectorStore
from app.config import config

# Use an in-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """
    Fixture to set up a temporary, in-memory SQLite database for a test function.
    """
    engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create the database tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the database tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_vector_store():
    """

    Fixture to set up a temporary vector store for a test function and clean it up afterward.
    """
    # Create a temporary directory for Chroma data
    temp_dir = tempfile.mkdtemp()
    
    # Patch the config to use the temporary directory
    with patch.dict(config, {"CHROMA_DATA_PATH": temp_dir}):
        # Reset the singleton instance of VectorStore to use the new path
        if 'instance' in VectorStore.__dict__:
            del VectorStore.instance
        
        vector_store_instance = VectorStore()
        yield vector_store_instance

    # Clean up the temporary directory
    shutil.rmtree(temp_dir)


@pytest.fixture
def tools_instance(test_db, test_vector_store):
    """
    Fixture to create a fully initialized Tools instance with a mock MCP
    and a real database session for integration testing.
    """
    mock_mcp = MagicMock()

    @contextmanager
    def mock_get_db(self):  # Add self to match the original method signature
        yield test_db

    # Patch the get_db method and the vector_store property on the Tools class
    with patch.object(Tools, 'get_db', mock_get_db), \
         patch.object(Tools, 'vector_store', new_callable=PropertyMock) as mock_vector_store:
        
        # Configure the mock property to return our test vector store instance
        mock_vector_store.return_value = test_vector_store
        
        # Create the Tools instance *after* the patches are in place
        tools = Tools(mock_mcp)
        yield tools
