"""Pytest configuration for SpaceDock tests.

Fixtures:
    client: Flask test client
"""
import os
import pytest
from KerbalStuff.app import app


@pytest.fixture(scope="session")
def flask_app():
    """Configure Flask app for testing."""
    app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    return app


@pytest.fixture(scope="function")
def client(flask_app):
    """Create test client."""
    return flask_app.test_client()