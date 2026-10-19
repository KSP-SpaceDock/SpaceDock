"""
Deployment configuration tests for SpaceDock.

This file contains tests for configuration files and settings.
"""

import pytest
from KerbalStuff.config import config, env


def test_config_loading():
    """Test that configuration is loaded correctly."""
    assert env == 'test'
    assert config.has_section(env)
    assert 'connection-string' in config[env]
    assert 'protocol' in config[env]
    assert 'domain' in config[env]


def test_database_connection_string():
    """Test database connection string configuration."""
    assert config[env]['connection-string'] == 'sqlite:///:memory:'


def test_protocol_and_domain():
    """Test protocol and domain configuration."""
    assert config[env]['protocol'] == 'https'
    assert config[env]['domain'] == 'tests.spacedock.info'


def test_profile_dir_not_set():
    """Test that profile directory is not set in test environment."""
    assert 'profile-dir' not in config[env]


def test_secret_key_present():
    """Test that secret key is present in configuration."""
    assert 'secret-key' in config[env]


def test_storage_directory():
    """Test storage directory configuration."""
    assert 'storage' in config[env]


def test_use_x_accel():
    """Test X-Accel configuration."""
    assert config[env]['use-x-accel'] == 'false'


def test_logging_configuration():
    """Test logging configuration."""
    assert 'logging' in config[env]
    assert config[env]['logging'] == 'logging.ini'


def test_debug_mode():
    """Test debug mode configuration."""
    assert config[env]['debug'] == 'false'


def test_celery_configuration():
    """Test Celery configuration."""
    assert 'celery-broker-url' in config[env]
    assert 'celery-result-backend' in config[env]
