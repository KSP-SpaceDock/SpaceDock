"""
Security input validation tests for SpaceDock.

This file contains tests for input validation and sanitization.
"""

import pytest
from flask.testing import FlaskClient
from flask import Response
from http import HTTPStatus
from KerbalStuff.objects import User, Mod
from KerbalStuff.database import db


def test_xss_prevention_in_mod_name(client: 'FlaskClient[Response]'):
    """Test that XSS attacks in mod names are prevented."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    
    # Login
    client.post('/login',
               data={'username': 'testuser',
                     'password': 'password123'})
    
    # Try to create a mod with XSS payload
    response = client.post('/mod/create',
                           data={'name': '<script>alert("XSS")</script>',
                                 'short_description': 'Test',
                                 'description': 'Test',
                                 'license': 'MIT'})
    assert response.status_code == HTTPStatus.OK
    
    # Verify the XSS payload is escaped in the response
    response = client.get('/mod/1')
    assert b'&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;' in response.data
    assert b'<script>alert("XSS")</script>' not in response.data


def test_sql_injection_prevention_in_search(client: 'FlaskClient[Response]'):
    """Test that SQL injection attacks in search queries are prevented."""
    # Try to search with SQL injection payload
    response = client.get('/api/search/mod?query=\' OR 1=1 --')
    assert response.status_code == HTTPStatus.OK
    # Should return results without executing the malicious query
    assert response.json == {'total': 0, 'count': 0, 'pages': 0, 'page': 1, 'result': []}


def test_input_validation_for_mod_creation(client: 'FlaskClient[Response]'):
    """Test input validation for mod creation."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    
    # Login
    client.post('/login',
               data={'username': 'testuser',
                     'password': 'password123'})
    
    # Try to create a mod with invalid data
    response = client.post('/mod/create',
                           data={'name': '',  # Empty name
                                 'short_description': 'Test',
                                 'description': 'Test',
                                 'license': 'MIT'})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b'Name is required' in response.data


def test_email_validation_in_registration(client: 'FlaskClient[Response]'):
    """Test email validation in user registration."""
    # Try to register with invalid email
    response = client.post('/register',
                           data={'username': 'newuser',
                                 'email': 'invalid-email',
                                 'password': 'password123'})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b'Invalid email address' in response.data


def test_password_strength_validation(client: 'FlaskClient[Response]'):
    """Test password strength validation."""
    # Try to register with weak password
    response = client.post('/register',
                           data={'username': 'newuser',
                                 'email': 'new@example.com',
                                 'password': 'weak'})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b'Password must be at least 12 characters' in response.data


def test_username_validation(client: 'FlaskClient[Response]'):
    """Test username validation."""
    # Try to register with invalid username
    response = client.post('/register',
                           data={'username': 'invalid username',  # Contains space
                                 'email': 'new@example.com',
                                 'password': 'password123'})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b'Username can only contain letters, numbers, and underscores' in response.data
