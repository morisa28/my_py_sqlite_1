"""Database connection, schema creation, and seed data initialization."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "library.db"
