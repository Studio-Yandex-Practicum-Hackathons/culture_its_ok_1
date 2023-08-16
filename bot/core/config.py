import os

from pydantic import Extra, Field
from pydantic_settings import BaseSettings

IN_DOCKER = os.getenv('AM_I_IN_A_DOCKER_CONTAINER', False) == 'YES'


class EnvBase(BaseSettings):
    class Config:
        env_file = None if IN_DOCKER else 'core/.env'
        extra = Extra.allow


class BotSettings(EnvBase):
    telegram_token: str


class PostgresSettings(EnvBase):
    db_name: str = Field(alias='POSTGRES_DB')
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    user: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')


class SentrySettings(EnvBase):
    sentry_dsn: str


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    postgres: PostgresSettings = PostgresSettings()
    sentry: SentrySettings = SentrySettings()


settings = Settings()
