import functools
import logging


def logger_factory(name):
    if name in ("debug", "d"):
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.DEBUG)
        return logging.debug("")
    if name in ("info", "i"):
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.INFO)
        return logging.info("")
    if name in ("warning", "w"):
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.WARNING)
        return logging.warning("")
    if name in ("error", "e"):
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.ERROR)
        return logging.error("")
    if name in ("critical", "c"):
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.CRITICAL)
        return logging.critical("")


def log_dec(logger_level):
    def wrap_func(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                logger_factory(logger_level)

        return wrapper

    return wrap_func
