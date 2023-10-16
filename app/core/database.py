from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass

metadata = MetaData()


sync_engine = create_engine(
    url=settings.database_url_psycopg,
    echo=True,
    pool_size=5,
    max_overflow=10
)

async_engine = create_async_engine(
    url=settings.database_url_asyncpg,
    echo=True
)

async_session = async_sessionmaker(async_engine)
sync_session = sessionmaker(sync_engine)


# Генератор для получения сессии
async def get_async_session():
    async with async_session() as session:
        yield session
