"""
config.py — Application configuration.

Centralizes all environment-specific settings. Adding a new environment
(e.g. staging) is a single class extension, not a widespread code change.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

    # Get the DATABASE_URL and fix the connection string for SQLAlchemy
    db_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'taskflow.db')}"
    )
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI key for AI summarisation (optional — falls back to heuristics)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    OPENAI_API_KEY = ""           # Never hit real API in tests


class ProductionConfig(Config):
    LOG_LEVEL = "WARNING"


# Map names → classes so the factory can pick the right one
config_map = {
    "development": Config,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
