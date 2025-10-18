from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_mcp():
    """Fixture to mock the mcp instance."""
    return MagicMock()

@pytest.fixture
def mock_db_session():
    """Fixture for a mock database session."""
    return MagicMock()

@pytest.fixture
def mock_vector_store_instance():
    """Fixture for a mock vector store instance."""
    return MagicMock()

@pytest.fixture
def mock_provider(mock_db_session, mock_vector_store_instance):
    """
    Fixture to mock the tool provider, which manages access to the
    database and vector store.
    """
    provider = MagicMock()

    @contextmanager
    def mock_get_db():
        yield mock_db_session

    provider.get_db = mock_get_db
    provider.vector_store = mock_vector_store_instance
    return provider
