from app.database import SessionLocal
from app.vector_store import VectorStore

# Create a singleton instance of the VectorStore
vector_store = VectorStore()

def get_db():
    """
    Dependency provider for the database session.
    Yields a new session for each request and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_vector_store():
    """
    Dependency provider for the vector store.
    Returns the singleton VectorStore instance.
    """
    return vector_store