from __future__ import annotations
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, JSON
from .config import config

Base = declarative_base()

def init_db():
    engine = create_engine(
        config["SQLALCHEMY_DATABASE_URL"], connect_args={"check_same_thread": False}
    )
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define SQLAlchemy models for Nodes and Edges
class NodeModel(Base):
    __tablename__ = "nodes"
    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)
    properties = Column(JSON, nullable=False)

class EdgeModel(Base):
    __tablename__ = "edges"
    id = Column(String, primary_key=True, index=True)
    source_id = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    label = Column(String, nullable=False)