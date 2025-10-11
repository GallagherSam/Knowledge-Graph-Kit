import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .config import config

# Constants
COLLECTION_NAME = "nodes"

def get_chroma_data_path() -> str:
    """Returns the Chroma data path from the config."""
    return config["CHROMA_DATA_PATH"]

def get_embedding_model() -> str:
    """Returns the embedding model from the config."""
    return config["EMBEDDING_MODEL"]


class VectorStore:
    """
    Manages all interactions with the ChromaDB vector store.
    """

    def __init__(self):
        """
        Initializes the VectorStore by setting up the ChromaDB client,
        the embedding function, and creating or getting the collection.
        """
        try:
            self.client = chromadb.PersistentClient(path=get_chroma_data_path(), settings=Settings(anonymized_telemetry=False))
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=get_embedding_model()
            )
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
            )
            logger.info("ChromaDB client and collection initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _generate_embedding_text(self, node: Dict[str, Any]) -> str:
        """
        Generates a combined text from a node's properties for embedding.

        Args:
            node: The node from which to generate the text.

        Returns:
            A string combining the node's type and relevant properties.
        """
        node_type = node.get("type", "")
        properties = node.get("properties", {})

        text_parts = [f"Type: {node_type}"]

        if "title" in properties:
            text_parts.append(f"Title: {properties['title']}")
        if "name" in properties:
            text_parts.append(f"Name: {properties['name']}")
        if "description" in properties:
            text_parts.append(f"Description: {properties['description']}")
        if "content" in properties:
            text_parts.append(f"Content: {properties['content']}")

        return ". ".join(text_parts)

    def add_node(self, node: Dict[str, Any]):
        """
        Adds a single node to the vector store.

        Args:
            node: The node to add.
        """
        try:
            text_for_embedding = self._generate_embedding_text(node)
            self.collection.add(
                documents=[text_for_embedding],
                metadatas=[{"type": node["type"]}],
                ids=[node["id"]],
            )
            logger.info(f"Node {node['id']} added to the vector store.")
        except Exception as e:
            logger.error(f"Failed to add node {node['id']} to vector store: {e}")

    def update_node(self, node: Dict[str, Any]):
        """
        Updates a node in the vector store.

        Args:
            node: The node to update.
        """
        try:
            text_for_embedding = self._generate_embedding_text(node)
            self.collection.update(
                documents=[text_for_embedding],
                metadatas=[{"type": node["type"]}],
                ids=[node["id"]],
            )
            logger.info(f"Node {node['id']} updated in the vector store.")
        except Exception as e:
            logger.error(f"Failed to update node {node['id']} in vector store: {e}")

    def delete_node(self, node_id: str):
        """
        Deletes a node from the vector store.

        Args:
            node_id: The ID of the node to delete.
        """
        try:
            self.collection.delete(ids=[node_id])
            logger.info(f"Node {node_id} deleted from the vector store.")
        except Exception as e:
            logger.error(f"Failed to delete node {node_id} from vector store: {e}")

    def semantic_search(
        self,
        query: str,
        node_type: Optional[str] = None,
        n_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Performs a semantic search for nodes in the vector store.

        Args:
            query: The query string to search for.
            node_type: An optional node type to filter the search by.
            n_results: The maximum number of results to return.

        Returns:
            A list of search results.
        """
        try:
            query_params = {
                "query_texts": [query],
                "n_results": n_results,
            }
            if node_type:
                query_params["where"] = {"type": node_type}

            results = self.collection.query(**query_params)
            logger.info(f"Semantic search completed for query: '{query}'")
            # The query returns a list of lists, so we take the first element.
            return results["ids"][0] if results and "ids" in results else []
        except Exception as e:
            logger.error(f"Semantic search failed for query '{query}': {e}")
            return []
