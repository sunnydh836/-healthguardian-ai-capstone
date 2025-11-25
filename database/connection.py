"""Database connection and initialization"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

# Base class for models
Base = declarative_base()

# Global engine and session maker
engine = None
AsyncSessionLocal = None


async def init_database():
    """Initialize database connection"""
    global engine, AsyncSessionLocal
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL not set, using SQLite in-memory database")
        database_url = "sqlite+aiosqlite:///:memory:"
    
    logger.info(f"Initializing database connection...")
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create session maker
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.success("Database initialized successfully")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database():
    """Close database connections"""
    global engine
    
    if engine:
        logger.info("Closing database connections...")
        await engine.dispose()
        logger.success("Database connections closed")
