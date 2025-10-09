import json
from pathlib import Path
from typing import List, Dict, Any

# Define the directory where data files are stored.
DATA_DIR = Path(__file__).parent.parent / "data"
NODES_FILE = DATA_DIR / "nodes.json"
EDGES_FILE = DATA_DIR / "edges.json"

class State:
    """
    A service class to manage the state of the knowledge graph by
    interacting with JSON files for nodes and edges.
    """

    def __init__(self):
        """
        Initializes the State manager. Ensures the data directory and
        the necessary JSON files exist.
        """
        self._initialize_state()

    def _initialize_state(self):
        """
        Creates the data directory and initial empty JSON files if they
        do not already exist.
        """
        DATA_DIR.mkdir(exist_ok=True)
        if not NODES_FILE.exists():
            with open(NODES_FILE, "w") as f:
                json.dump([], f)
        if not EDGES_FILE.exists():
            with open(EDGES_FILE, "w") as f:
                json.dump([], f)

    def read_nodes(self) -> List[Dict[str, Any]]:
        """
        Reads and returns all nodes from the nodes.json file.

        Returns:
            A list of nodes, where each node is a dictionary.
        """
        with open(NODES_FILE, "r") as f:
            return json.load(f)

    def write_nodes(self, nodes: List[Dict[str, Any]]):
        """
        Writes a list of nodes to the nodes.json file.

        Args:
            nodes: A list of node dictionaries to write to the file.
        """
        with open(NODES_FILE, "w") as f:
            json.dump(nodes, f, indent=4)

    def read_edges(self) -> List[Dict[str, Any]]:
        """
        Reads and returns all edges from the edges.json file.

        Returns:
            A list of edges, where each edge is a dictionary.
        """
        with open(EDGES_FILE, "r") as f:
            return json.load(f)

    def write_edges(self, edges: List[Dict[str, Any]]):
        """
        Writes a list of edges to the edges.json file.

        Args:
            edges: A list of edge dictionaries to write to the file.
        """
        with open(EDGES_FILE, "w") as f:
            json.dump(edges, f, indent=4)

# Create a singleton instance to be used by other modules
state_manager = State()
