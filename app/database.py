from __future__ import annotations

from sqlalchemy import JSON, Column, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def init_db(database_url: str):
    """
    Initializes the database connection and creates tables if they don't exist.

    Args:
        database_url: The SQLAlchemy database connection URL

    Returns:
        A sessionmaker factory for creating database sessions.
    """
    engine = create_engine(
        database_url, connect_args={"check_same_thread": False}
    )

    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define SQLAlchemy models for Nodes and Edges
class NodeModel(Base):
    __tablename__ = "nodes"
    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True)  # Indexed for type filtering
    properties = Column(JSON, nullable=False)

class EdgeModel(Base):
    __tablename__ = "edges"
    id = Column(String, primary_key=True, index=True)
    source_id = Column(String, nullable=False, index=True)  # Indexed for graph traversal
    target_id = Column(String, nullable=False, index=True)  # Indexed for graph traversal
    label = Column(String, nullable=False, index=True)  # Indexed for label filtering