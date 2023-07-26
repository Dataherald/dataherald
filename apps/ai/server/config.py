import os

from dotenv import load_dotenv

load_dotenv()

DB_ALIAS = os.environ.get("DB_ALIAS", "v2_real_estate")

K2_CORE_URL = os.environ.get("K2_CORE_URL")
MONGODB_URI = os.environ.get("MONGO_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
DEFAULT_K2_TIMEOUT = os.environ.get("DEFAULT_TIMEOUT")
