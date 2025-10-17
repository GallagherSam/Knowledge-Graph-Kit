import json
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration with validation and immutability."""

    SQLALCHEMY_DATABASE_URL: str = Field(
        default="sqlite:///./graph.db",
        description="Database connection URL"
    )
    CHROMA_DATA_PATH: str = Field(
        default="chroma_data",
        description="Path for ChromaDB storage"
    )
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model name"
    )
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    PORT: int = Field(
        default=8000,
        description="Server port number",
        ge=1,
        le=65535
    )

    model_config = {
        # Makes the config immutable
        "frozen": True,
        # Allow loading from .env files
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from JSON file or environment variables.

    Args:
        config_path: Optional path to JSON config file. If provided, loads from JSON.
                    If None, loads from environment variables or uses defaults.

    Returns:
        Immutable AppConfig instance with validated configuration.

    Raises:
        json.JSONDecodeError: If the config file contains invalid JSON.
    """
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
                return AppConfig(**config_dict)
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {config_path}. Using defaults and environment variables.")
            return AppConfig()
        except json.JSONDecodeError as e:
            print(f"Error: Could not decode JSON from {config_path}: {e}")
            raise
    else:
        # Load from environment variables or use defaults
        return AppConfig()
