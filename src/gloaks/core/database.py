from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os

# Use aiosqlite for async support
# If using Postgres, use 'postgresql+asyncpg://...'
DATABASE_URL = os.getenv("GLOAKS_DATABASE_URL", "sqlite+aiosqlite:///./gloaks.db")

# check_same_thread=False is not needed for aiosqlite usually but doesn't hurt if passed to args?
# Actually async engine takes specific args.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=connect_args)

async def create_db_and_tables():
    """Create database tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting an async database session."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
