from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import config

def get_database_url() -> str:
    """Returns the database URL from the config."""
    return config.get_database_url()

# For SQLite, we need to ensure that the same thread is used for all operations.
# For other databases, we don't need this argument.
engine_args = {}
if config.DB_TYPE == 'sqlite':
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    get_database_url(), **engine_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()