import json
from typing import Dict, Any

# Global variable to hold the configuration
config: Dict[str, Any] = {}

def load_config(path: str):
    """
    Loads the configuration from a JSON file and populates the global config object.

    Args:
        path: The path to the configuration file.
    """
    global config
    try:
        with open(path, 'r') as f:
            config.update(json.load(f))
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at {path}. Using default values.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {path}. Please check the file format.")
        raise