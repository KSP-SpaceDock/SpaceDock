"""
Backend service tests for SpaceDock.

This file contains unit tests for business logic and services.
"""

import pytest
from unittest.mock import patch, MagicMock
from KerbalStuff.objects import User, Mod
from KerbalStuff.services import mod_service, user_service


def test_mod_service_create_mod():
    """Test mod service create mod functionality."""
    with patch('KerbalStuff.services.mod_service.db') as mock_db:
        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()
        
        user = User(username="testuser", email="test@example.com")
        mod_data = {
            "name": "Test Mod",
            "short_description": "A test mod",
            "description": "This is a test mod.",
            "license": "MIT",
        }
        
        result = mod_service.create_mod(user, mod_data)
        assert result.name == "Test Mod"
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()


def test_user_service_create_user():
    """Test user service create user functionality."""
    with patch('KerbalStuff.services.user_service.db') as mock_db:
        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()
        
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        }
        
        result = user_service.create_user(user_data)
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.check_password("password123") is True
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()


def test_mod_service_get_mod_by_id():
    """Test mod service get mod by id functionality."""
    with patch('KerbalStuff.services.mod_service.Mod') as mock_mod:
        mock_mod.query.filter_by.return_value.first.return_value = Mod(
            id=1,
            name="Test Mod",
            short_description="A test mod",
        )
        
        result = mod_service.get_mod_by_id(1)
        assert result.id == 1
        assert result.name == "Test Mod"


def test_user_service_get_user_by_username():
    """Test user service get user by username functionality."""
    with patch('KerbalStuff.services.user_service.User') as mock_user:
        mock_user.query.filter_by.return_value.first.return_value = User(
            username="testuser",
            email="test@example.com",
        )
        
        result = user_service.get_user_by_username("testuser")
        assert result.username == "testuser"
        assert result.email == "test@example.com"
