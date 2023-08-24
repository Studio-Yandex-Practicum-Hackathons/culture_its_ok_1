import logging
import os
import pathlib
from pathlib import Path

import sentry_sdk
from pydantic import Extra, Field
from pydantic_settings import BaseSettings

IN_DOCKER: bool = os.getenv('AM_I_IN_A_DOCKER_CONTAINER', False) == 'YES'

BASE_DIR: pathlib.Path = Path(__file__).parent.parent
LOG_DIR: pathlib.Path = BASE_DIR / 'logs'
MEDIA_DIR: pathlib.Path = BASE_DIR / 'media'


class EnvBase(BaseSettings):
    class Config:
        env_file = None if IN_DOCKER else '.env'
        extra = Extra.allow


class BotSettings(EnvBase):
    telegram_token: str
    debug: bool
    words_per_minute: int = 250  # скорость чтения текста, слов в минуту
    photo_showing_delay: int = 5  # задержка в секундах при показе фотографий


class PostgresSettings(EnvBase):
    db_name: str = Field(alias='POSTGRES_DB')
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    user: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')


class SentrySettings(EnvBase):
    dsn: str = Field(alias='SENTRY_DSN')

    def init_sentry(self):
        sentry_sdk.init(dsn=self.dsn)


class LoggingSettings(EnvBase):
    log_file: pathlib.Path = LOG_DIR / 'bot.log'
    log_format: str = '"%(asctime)s - [%(levelname)s] - %(message)s"'
    dt_format: str = '%d.%m.%Y %H:%M:%S'
    debug: bool

    def init_global_logging_level(self):
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.CRITICAL
        )


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    postgres: PostgresSettings = PostgresSettings()
    sentry: SentrySettings = SentrySettings()
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
