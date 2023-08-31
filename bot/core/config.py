import logging
import os
import pathlib
from datetime import timedelta
from pathlib import Path

import sentry_sdk
from pydantic import Extra, Field, SecretStr
from pydantic_settings import BaseSettings

IN_DOCKER: bool = os.getenv('AM_I_IN_A_DOCKER_CONTAINER', False) == 'YES'

BASE_DIR: pathlib.Path = Path(__file__).parent.parent
LOG_DIR: pathlib.Path = BASE_DIR / 'logs'
MEDIA_DIR: pathlib.Path = BASE_DIR / 'media'
VOICE_DIR: pathlib.Path = MEDIA_DIR / 'voice'

USER_DATA_TTL = timedelta(days=1)


class EnvBase(BaseSettings):
    class Config:
        env_file = None if IN_DOCKER else '.env'
        extra = Extra.ignore


class BotSettings(EnvBase):
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        os.makedirs(MEDIA_DIR, exist_ok=True)
        os.makedirs(VOICE_DIR, exist_ok=True)
        super().__init__()

    telegram_token: str
    debug: bool
    storage_ttl: timedelta = USER_DATA_TTL
    admin_password: SecretStr
    reading_speed: int
    photo_show_delay: int
    reflection_text_limit: int
    reflection_voice_limit: int
    survey_url: str


class LoggingSettings(EnvBase):
    log_file: pathlib.Path = LOG_DIR / 'bot.log'
    log_format: str = '"%(asctime)s - [%(levelname)s] - %(message)s"'
    dt_format: str = '%d.%m.%Y %H:%M:%S'
    debug: bool

    def init_global_logging_level(self):
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.CRITICAL
        )


class PostgresSettings(EnvBase):
    db_name: str = Field(alias='POSTGRES_DB')
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    user: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')


class RedisSettings(EnvBase):
    host: str = Field(alias='REDIS_HOST')
    port: int = Field(alias='REDIS_PORT')


class SentrySettings(EnvBase):
    dsn: str = Field(alias='SENTRY_DSN')

    def init_sentry(self):
        sentry_sdk.init(dsn=self.dsn)


class GoogleInfo(EnvBase):
    type: str = ''  # noqa: VNE003
    project_id: str = ''
    private_key_id: str = ''
    private_key: str = ''
    client_email: str = ''
    client_id: str = ''
    auth_uri: str = ''
    token_uri: str = ''
    auth_provider_x509_cert_url: str = ''
    client_x509_cert_url: str = ''


class GoogleSettings(EnvBase):
    info: GoogleInfo = GoogleInfo()
    spreadsheet_url: str
    scopes: list[str] = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]


class Settings(BaseSettings):
    bot: BotSettings = BotSettings()
    logging: LoggingSettings = LoggingSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    sentry: SentrySettings = SentrySettings()
    google: GoogleSettings = GoogleSettings()


settings = Settings()
