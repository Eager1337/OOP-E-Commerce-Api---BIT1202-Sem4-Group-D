"""
Database configuration with SQLAlchemy async ORM.
Implements dependency injection pattern for database sessions.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Lazy initialization of engine and session factory
_engine = None
_AsyncSessionLocal = None


def _get_engine():
    """Lazily create and return the async engine."""
    global _engine
    if _engine is None:
        try:
            _engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
                future=True,
                poolclass=NullPool  # Recommended for async applications
            )
        except ModuleNotFoundError as e:
            msg = (
                f"Database driver error: {e}\n"
                "Make sure the database driver for your DATABASE_URL is installed."
            )
            logger.error(msg)
            raise RuntimeError(msg) from e
    return _engine


def _get_session_factory():
    """Lazily create and return the async session factory."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _AsyncSessionLocal


# Create stubs that don't fail at import time
engine = None  # Will be initialized on first use
AsyncSessionLocal = None  # Will be initialized on first use

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency injection function for database sessions.
    Yields an async session and ensures proper cleanup.

    Usage: Depends(get_db) in route handlers.
    """
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (for development/testing)."""
    # Import all models to register them with SQLAlchemy Base
    from app.models import User, Category, Product, Order, OrderItem, Review
    
    # If using sqlite+aiosqlite, create tables using the synchronous
    # engine to avoid requiring the 'greenlet' extension at startup.
    if settings.DATABASE_URL.startswith("sqlite+aiosqlite"):
        from sqlalchemy import create_engine as create_sync_engine
        import asyncio

        sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

        def _create_tables():
            sync_engine = create_sync_engine(sync_url)
            Base.metadata.create_all(sync_engine)
            sync_engine.dispose()

        try:
            await asyncio.get_event_loop().run_in_executor(None, _create_tables)
            logger.info("✓ SQLite tables initialized (sync path)")
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize SQLite tables: {e}")
        return

    try:
        async with _get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Database tables initialized successfully")
    except RuntimeError as e:
        if "Database driver not available" in str(e):
            logger.warning(f"⚠️  Database driver not available - skipping initialization. {str(e)}")
        else:
            raise
    except ModuleNotFoundError as e:
        logger.warning(f"⚠️  Database driver not available - skipping initialization. {e}")


async def close_db():
    """Close database connections."""
    try:
        await _get_engine().dispose()
        logger.info("✓ Database connections closed")
    except (RuntimeError, ModuleNotFoundError) as e:
        if "Database driver not available" in str(e) or "No module named" in str(e):
            logger.debug(f"Database not initialized - nothing to close")
        else:
            raise
