import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST_TEST = os.getenv("DB_HOST_TEST")
DB_PORT_TEST = os.getenv("DB_PORT_TEST")
DB_NAME_TEST = os.getenv("DB_NAME_TEST")
DB_USER_TEST = os.getenv("DB_USER_TEST")
DB_PASS_TEST = os.getenv("DB_PASS_TEST")
