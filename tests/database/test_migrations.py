"""
Database migration tests for SpaceDock.

This file contains tests for database migrations.
"""

import pytest
from alembic.config import Config
from alembic import command
from KerbalStuff.database import create_database, drop_database


@pytest.fixture
def alembic_config():
    """Create an Alembic configuration for testing."""
    config = Config()
    config.set_main_option('script_location', 'alembic')
    config.set_main_option('sqlalchemy.url', 'sqlite:///:memory:')
    return config


def test_migrations_alembic_history(alembic_config):
    """Test that Alembic can generate the migration history."""
    create_database()
    try:
        # Stamp the database with the latest migration
        command.stamp(alembic_config, 'head')
        
        # Get the current migration head
        result = command.current(alembic_config)
        assert result is not None
    finally:
        drop_database()


def test_migrations_alembic_upgrade(alembic_config):
    """Test that Alembic can upgrade the database."""
    create_database()
    try:
        # Upgrade to the latest migration
        command.upgrade(alembic_config, 'head')
        
        # Verify the upgrade was successful
        result = command.current(alembic_config)
        assert result is not None
    finally:
        drop_database()


def test_migrations_alembic_downgrade(alembic_config):
    """Test that Alembic can downgrade the database."""
    create_database()
    try:
        # Upgrade to the latest migration
        command.upgrade(alembic_config, 'head')
        
        # Downgrade to the base migration
        command.downgrade(alembic_config, 'base')
        
        # Verify the downgrade was successful
        result = command.current(alembic_config)
        assert result == 'base'
    finally:
        drop_database()
