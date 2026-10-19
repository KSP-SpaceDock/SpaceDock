"""
Security authentication tests for SpaceDock.

This file contains tests for authentication functionality.
"""

import pytest
from flask.testing import FlaskClient
from flask import Response
from http import HTTPStatus
from KerbalStuff.objects import User
from KerbalStuff.database import db


@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def test_login_success(client: 'FlaskClient[Response]', test_user):
    """Test successful user login."""
    response = client.post('/login',
                           data={'username': 'testuser',
                                 'password': 'password123'},
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b'Welcome, testuser' in response.data


def test_login_failure(client: 'FlaskClient[Response]', test_user):
    """Test failed user login with incorrect credentials."""
    response = client.post('/login',
                           data={'username': 'testuser',
                                 'password': 'wrongpassword'},
                           follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b'Invalid username or password' in response.data


def test_logout(client: 'FlaskClient[Response]', test_user):
    """Test user logout."""
    # Login first
    client.post('/login',
               data={'username': 'testuser',
                     'password': 'password123'})
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == HTTPStatus.OK
    assert b'Logged out successfully' in response.data


def test_password_reset_request(client: 'FlaskClient[Response]', test_user):
    """Test password reset request."""
    response = client.post('/request-reset',
                           data={'email': 'test@example.com'})
    assert response.status_code == HTTPStatus.OK
    assert b'Check your email for instructions' in response.data


def test_password_reset_with_token(client: 'FlaskClient[Response]', test_user):
    """Test password reset with token."""
    # Request reset first
    client.post('/request-reset',
               data={'email': 'test@example.com'})
    
    # Use token to reset password (simplified for testing)
    response = client.post('/reset-password',
                           data={'token': 'fake-token',
                                 'password': 'newpassword123'})
    assert response.status_code == HTTPStatus.OK
    assert b'Your password has been updated' in response.data
