from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# SQLite by default, can be overridden by env var
DATABASE_URL = os.getenv("GLOAKS_DATABASE_URL", "sqlite:///./gloaks.db")

# check_same_thread=False is needed for SQLite with FastAPI/asyncio
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    with Session(engine) as session:
        yield session
