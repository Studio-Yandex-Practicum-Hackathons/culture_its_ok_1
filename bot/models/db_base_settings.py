from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from bot.core.config import settings

DATABASE_URL_TEMPLATE = (
    '{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'
)

sqlalchemy_url = DATABASE_URL_TEMPLATE.format(
    dialect='postgresql',
    driver='asyncpg',
    user=settings.postgres.user,
    password=settings.postgres.password,
    host=settings.postgres.host,
    port=settings.postgres.port,
    db_name=settings.postgres.db_name
)


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(sqlalchemy_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session():

    async with AsyncSessionLocal() as async_session:

        yield async_session
