"""
tests/conftest.py — Pytest fixtures shared across all test modules.

Uses the TestingConfig which points to an in-memory SQLite database.
Each test gets a fresh app context + clean database to prevent test pollution.
"""

import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    """Create a test application instance once per session."""
    application = create_app("testing")
    return application


@pytest.fixture(scope="function")
def client(app):
    """
    HTTP test client with a fresh DB for each test.

    Rolling back after each test instead of truncating is faster
    for SQLite and guarantees isolation without re-seeding.
    """
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide the db instance within an app context."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
