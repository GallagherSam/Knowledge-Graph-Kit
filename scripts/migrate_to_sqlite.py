import json
import sys
import uuid
from pathlib import Path

# Add the project root to the Python path to allow for imports from the 'app' module.
sys.path.append(str(Path(__file__).parent.parent))

from app.state import state_manager

# Define the directory where the original JSON data files are stored.
DATA_DIR = Path(__file__).parent.parent / "data"
NODES_FILE = DATA_DIR / "nodes.json"
EDGES_FILE = DATA_DIR / "edges.json"

def migrate_data():
    """
    Migrates data from JSON files to the SQLite database.
    """
    print("Starting data migration...")

    # Read nodes from the JSON file and write them to the database.
    if NODES_FILE.exists():
        with open(NODES_FILE, "r") as f:
            nodes_data = json.load(f)
        if nodes_data:
            print(f"Migrating {len(nodes_data)} nodes...")
            for node in nodes_data:
                state_manager.add_node(node)
            print("Nodes migration complete.")
        else:
            print("No nodes to migrate.")
    else:
        print("nodes.json not found. Skipping node migration.")

    # Read edges from the JSON file, add a UUID to each, and write them to the database.
    if EDGES_FILE.exists():
        with open(EDGES_FILE, "r") as f:
            edges_data = json.load(f)
        if edges_data:
            print(f"Migrating {len(edges_data)} edges...")
            for edge in edges_data:
                edge['id'] = str(uuid.uuid4())
                state_manager.add_edge(edge)
            print("Edges migration complete.")
        else:
            print("No edges to migrate.")
    else:
        print("edges.json not found. Skipping edge migration.")

    print("Data migration finished.")

if __name__ == "__main__":
    migrate_data()