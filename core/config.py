import os

import sentry_sdk
from dotenv import load_dotenv

load_dotenv()


def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
    )
