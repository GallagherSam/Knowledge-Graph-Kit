from sqlalchemy import Column, String, JSON
from app.database import Base

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