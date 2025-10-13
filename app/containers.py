from dependency_injector import containers, providers

from app.database import SessionLocal
from app.vector_store import VectorStore

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Resource(get_db_session)
    vector_store = providers.Singleton(VectorStore)