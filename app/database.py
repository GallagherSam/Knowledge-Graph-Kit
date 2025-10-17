from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, JSON
from .config import config

Base = declarative_base()

def init_db():
    """
    Initializes the database connection and creates tables if they don't exist.

    Returns:
        A sessionmaker factory for creating database sessions.
    """
    engine = create_engine(
        config["SQLALCHEMY_DATABASE_URL"], connect_args={"check_same_thread": False}
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