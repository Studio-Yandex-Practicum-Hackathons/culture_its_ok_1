import asyncio

from core.config import settings
from core.logger import log_dec, logger_factory


@log_dec(logger=logger_factory(__name__))
async def main():
    pass


if __name__ == "__main__":
    settings.sentry.init_sentry()
    asyncio.run(main())
