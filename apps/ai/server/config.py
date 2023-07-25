import os

from dotenv import load_dotenv

load_dotenv()

K2_CORE_URL = os.environ.get("K2_CORE_URL")
MONGODB_URI = os.environ.get("MONGO_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")
DEFAULT_K2_TIMEOUT = os.environ.get("DEFAULT_TIMEOUT")
