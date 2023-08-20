from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from core.config import settings

DATABASE_URL_TEMPLATE = (
    '{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'
)

SQLALCHEMY_URL = DATABASE_URL_TEMPLATE.format(
    dialect='postgresql',
    driver='asyncpg',
    **settings.postgres.model_dump(),
)


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return f'culture_{cls.__name__.lower()}'

    id = Column(Integer, primary_key=True, autoincrement=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(SQLALCHEMY_URL)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
