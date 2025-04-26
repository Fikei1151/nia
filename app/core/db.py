from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings
import logging

logger = logging.getLogger(__name__)

if not settings.database_url or settings.database_url.startswith("postgresql+asyncpg://user:password"):
    logger.warning("DATABASE_URL is not configured properly in .env file.")
    DATABASE_URL = None
else:
    DATABASE_URL = settings.database_url

if DATABASE_URL:
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        AsyncSessionFactory = async_sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        logger.info("Database engine and session factory created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database engine or session factory: {e}")
        engine = None
        AsyncSessionFactory = None
else:
    engine = None
    AsyncSessionFactory = None

Base = declarative_base()

async def get_db_session() -> AsyncSession:
    if not AsyncSessionFactory:
        raise RuntimeError("Database session factory is not initialized. Check DATABASE_URL.")
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def create_db_and_tables():
    if not engine:
        logger.error("Database engine is not initialized. Cannot create tables.")
        return
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables checked/created successfully.")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}") 