from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    DB_TYPE: Literal['sqlite', 'postgres'] = 'sqlite'
    SQLALCHEMY_DATABASE_URL: Optional[str] = "sqlite:///./graph.db"
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_DB: Optional[str] = None

    CHROMA_TYPE: Literal['local', 'hosted'] = 'local'
    CHROMA_DATA_PATH: Optional[str] = "chroma_data"
    CHROMA_HOST: Optional[str] = None
    CHROMA_PORT: Optional[int] = None

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    def get_database_url(self) -> str:
        if self.DB_TYPE == 'postgres':
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return self.SQLALCHEMY_DATABASE_URL

config = Settings()

def load_config(path: str):
    """
    Loads the configuration from a .env file, populating the global config object.

    Args:
        path: The path to the configuration file.
    """
    global config
    config = Settings(_env_file=path)