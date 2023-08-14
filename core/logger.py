import functools
import logging


def logger_factory(name):
    if name in ("debug", "d"):
        return logging.debug("")
    if name in ("info", "i"):
        return logging.info("")
    if name in ("warning", "w"):
        return logging.warning("")
    if name in ("error", "e"):
        return logging.error("")
    if name in ("critical", "c"):
        return logging.critical("")


def log_dec(logger):
    def wrap_func(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger_factory(logger)
            return func(*args, **kwargs)

        return wrapper

    return wrap_func
