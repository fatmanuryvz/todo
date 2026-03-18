import warnings

from dotenv import load_dotenv
from starlette.config import Config

warnings.filterwarnings("ignore", message="Config file '.env' not found.")

load_dotenv("local.env")

config = Config(".env")


# Postgres DB
POSTGRES_IP = config('POSTGRES_IP', cast=str)
POSTGRES_PORT = config('POSTGRES_PORT', cast=int)
POSTGRES_DB = config('POSTGRES_DB', cast=str)
POSTGRES_USERNAME = config('POSTGRES_USERNAME', cast=str)
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD', cast=str)

SECRET_KEY = config('SECRET_KEY', cast=str)
ALGORITHM = config('ALGORITHM', cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=str)


# Redis
REDIS_HOST = config('REDIS_HOST', cast=str)
