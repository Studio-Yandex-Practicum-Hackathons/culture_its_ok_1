from pydantic import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str

    class Config:
        env_file = './env/.bot.env'


class PostgresSettings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = './env/.postgres.env'


class SentrySettings(BaseSettings):
    sentry_dsn: str

    class Config:
        env_file = './env/.sentry.env'


bot_settings = BotSettings()
postgres_settings = PostgresSettings()
sentry_settings = SentrySettings()
