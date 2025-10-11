import json
from typing import Dict, Any

DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URL": "sqlite:///./graph.db",
    "CHROMA_DATA_PATH": "chroma_data",
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    "HOST": "0.0.0.0",
    "PORT": 8000,
}

# Global variable to hold the configuration
config: Dict[str, Any] = {}

def load_config(path: str):
    """
    Loads the configuration from a JSON file, populating the global config object.
    It starts with default values and overrides them with any values from the file.

    Args:
        path: The path to the configuration file.
    """
    global config
    
    # Start with a copy of the default configuration
    temp_config = DEFAULT_CONFIG.copy()

    try:
        with open(path, 'r') as f:
            file_config = json.load(f)
            temp_config.update(file_config)
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at {path}. Using default values.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {path}. Please check the file format.")
        raise
    
    # Update the global config object
    config.update(temp_config)