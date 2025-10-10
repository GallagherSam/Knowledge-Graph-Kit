from typing import List, Dict, Any, Optional

from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal

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

class State:
    """
    A service class to manage the state of the knowledge graph by
    interacting with a SQLite database.
    """

    def __init__(self):
        """
        Initializes the State manager. Ensures the database and
        the necessary tables exist.
        """
        self._initialize_state()

    def _initialize_state(self):
        """
        Creates the database and tables if they do not already exist.
        """
        Base.metadata.create_all(bind=engine)

    def _db_session(self) -> Session:
        """
        Provides a new database session.
        """
        return SessionLocal()

    def add_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a single node to the database.

        Args:
            node_data: A dictionary representing the node.

        Returns:
            The created node as a dictionary.
        """
        with self._db_session() as db:
            db_node = NodeModel(**node_data)
            db.add(db_node)
            db.commit()
            db.refresh(db_node)
            return {"id": db_node.id, "type": db_node.type, "properties": db_node.properties}

    def update_node_in_db(self, node_id: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a node's properties in the database.

        Args:
            node_id: The ID of the node to update.
            properties: The new properties for the node.

        Returns:
            The updated node as a dictionary, or None if not found.
        """
        with self._db_session() as db:
            db_node = db.query(NodeModel).filter(NodeModel.id == node_id).first()
            if db_node:
                db_node.properties = properties
                db.commit()
                db.refresh(db_node)
                return {"id": db_node.id, "type": db_node.type, "properties": db_node.properties}
            return None

    def delete_node(self, node_id: str) -> bool:
        """
        Deletes a node and its connected edges from the database.

        Args:
            node_id: The ID of the node to delete.

        Returns:
            True if the node was deleted, False otherwise.
        """
        with self._db_session() as db:
            db_node = db.query(NodeModel).filter(NodeModel.id == node_id).first()
            if db_node:
                db.delete(db_node)
                # Also delete connected edges
                db.query(EdgeModel).filter((EdgeModel.source_id == node_id) | (EdgeModel.target_id == node_id)).delete(synchronize_session=False)
                db.commit()
                return True
            return False

    def add_edge(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a single edge to the database.

        Args:
            edge_data: A dictionary representing the edge.

        Returns:
            The created edge as a dictionary.
        """
        with self._db_session() as db:
            db_edge = EdgeModel(**edge_data)
            db.add(db_edge)
            db.commit()
            db.refresh(db_edge)
            return {"id": db_edge.id, "source_id": db_edge.source_id, "target_id": db_edge.target_id, "label": db_edge.label}

    def delete_edge(self, edge_id: str) -> bool:
        """
        Deletes an edge from the database.

        Args:
            edge_id: The ID of the edge to delete.

        Returns:
            True if the edge was deleted, False otherwise.
        """
        with self._db_session() as db:
            db_edge = db.query(EdgeModel).filter(EdgeModel.id == edge_id).first()
            if db_edge:
                db.delete(db_edge)
                db.commit()
                return True
            return False

    def read_nodes(self) -> List[Dict[str, Any]]:
        """
        Reads and returns all nodes from the database.

        Returns:
            A list of nodes, where each node is a dictionary.
        """
        with self._db_session() as db:
            nodes = db.query(NodeModel).all()
            return [{"id": n.id, "type": n.type, "properties": n.properties} for n in nodes]

    def read_edges(self) -> List[Dict[str, Any]]:
        """
        Reads and returns all edges from the database.

        Returns:
            A list of edges, where each edge is a dictionary.
        """
        with self._db_session() as db:
            edges = db.query(EdgeModel).all()
            return [{"id": e.id, "source_id": e.source_id, "target_id": e.target_id, "label": e.label} for e in edges]

# Create a singleton instance to be used by other modules
state_manager = State()