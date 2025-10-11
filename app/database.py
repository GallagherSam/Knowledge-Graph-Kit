from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import config

def get_database_url() -> str:
    """Returns the database URL from the config."""
    return config["SQLALCHEMY_DATABASE_URL"]

engine = create_engine(
    get_database_url(), connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()