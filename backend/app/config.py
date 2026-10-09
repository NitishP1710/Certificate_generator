import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

raw_database_url = os.getenv("DATABASE_URL")
if not raw_database_url:
	raise RuntimeError(
		"DATABASE_URL is required. Set it to the hosted PostgreSQL connection string."
	)

APP_ENV = os.getenv("APP_ENV", "development")
if raw_database_url.startswith("sqlite") and APP_ENV != "test":
	raise RuntimeError(
		"SQLite is only supported during tests. Configure DATABASE_URL with a hosted PostgreSQL database."
	)

# Some hosted providers still return the legacy postgres:// scheme.
DATABASE_URL = raw_database_url.replace("postgres://", "postgresql+psycopg2://", 1)
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret")
FILE_STORAGE_PATH = Path(os.getenv("FILE_STORAGE_PATH", str(BASE_DIR / "storage"))).resolve()

FILE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
