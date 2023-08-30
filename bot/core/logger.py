import functools
import logging
from functools import cache
from logging.handlers import RotatingFileHandler
from sys import stdout

import sentry_sdk
from core.config import settings


@cache
def logger_factory(name: str) -> logging.Logger:
    """Генерирует преднастроенный логгер по заданному имени."""
    logger = logging.getLogger(name)

    logger.setLevel(
        logging.DEBUG if settings.logging.debug else logging.CRITICAL
    )

    c_handler = logging.StreamHandler(stdout)
    f_handler = RotatingFileHandler(filename=settings.logging.log_file,
                                    maxBytes=10**6,
                                    backupCount=5,
                                    encoding='UTF-8')

    formatter = logging.Formatter(fmt=settings.logging.log_format,
                                  datefmt=settings.logging.dt_format)
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


def log_exceptions(logger: logging.Logger):
    """Декоратор для логгирования ошибок в log-файл и Sentry"""
    def wrap_func(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if settings.bot.debug:
                logger.info(f'handled by {func.__name__}')
            try:
                return await func(*args, **kwargs)
            except Exception as exception:  # noqa: B902
                logger.exception(msg=f'Исключение в функции {func.__name__}')
                sentry_sdk.capture_exception(exception)
                raise

        return wrapper

    return wrap_func
