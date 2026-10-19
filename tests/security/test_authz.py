"""
Security authorization tests for SpaceDock.

This file contains tests for authorization and permission checks.
"""

import pytest
from flask.testing import FlaskClient
from flask import Response
from http import HTTPStatus
from KerbalStuff.objects import User, Mod
from KerbalStuff.database import db


@pytest.fixture
def admin_user():
    """Create an admin user for authorization tests."""
    user = User(username="admin", email="admin@example.com", role="admin")
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user():
    """Create a regular user for authorization tests."""
    user = User(username="user", email="user@example.com", role="user")
    user.set_password("user123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def mod_by_regular_user(regular_user):
    """Create a mod owned by a regular user."""
    mod = Mod(name="User's Mod", user=regular_user, published=True)
    db.session.add(mod)
    db.session.commit()
    return mod


def test_admin_access_protected_route(client: 'FlaskClient[Response]', admin_user):
    """Test admin access to protected routes."""
    # Login as admin
    client.post('/login',
               data={'username': 'admin',
                     'password': 'admin123'})
    
    # Access admin-only route
    response = client.get('/admin/dashboard')
    assert response.status_code == HTTPStatus.OK
    assert b'Admin Dashboard' in response.data


def test_regular_user_cannot_access_admin_route(client: 'FlaskClient[Response]', regular_user):
    """Test that regular users cannot access admin routes."""
    # Login as regular user
    client.post('/login',
               data={'username': 'user',
                     'password': 'user123'})
    
    # Try to access admin-only route
    response = client.get('/admin/dashboard')
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_mod_owner_can_edit_mod(client: 'FlaskClient[Response]', regular_user, mod_by_regular_user):
    """Test that mod owners can edit their mods."""
    # Login as mod owner
    client.post('/login',
               data={'username': 'user',
                     'password': 'user123'})
    
    # Edit the mod
    response = client.post(f'/mod/{mod_by_regular_user.id}/edit',
                           data={'name': 'Updated Mod Name'})
    assert response.status_code == HTTPStatus.OK


def test_non_owner_cannot_edit_mod(client: 'FlaskClient[Response]', admin_user, mod_by_regular_user):
    """Test that non-owners cannot edit mods."""
    # Login as admin (not the mod owner)
    client.post('/login',
               data={'username': 'admin',
                     'password': 'admin123'})
    
    # Try to edit the mod
    response = client.post(f'/mod/{mod_by_regular_user.id}/edit',
                           data={'name': 'Updated Mod Name'})
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_admin_can_delete_any_mod(client: 'FlaskClient[Response]', admin_user, mod_by_regular_user):
    """Test that admins can delete any mod."""
    # Login as admin
    client.post('/login',
               data={'username': 'admin',
                     'password': 'admin123'})
    
    # Delete the mod
    response = client.post(f'/mod/{mod_by_regular_user.id}/delete')
    assert response.status_code == HTTPStatus.OK


def test_regular_user_cannot_delete_other_mods(client: 'FlaskClient[Response]', regular_user, mod_by_regular_user):
    """Test that regular users cannot delete other users' mods."""
    # Login as regular user (not the mod owner)
    client.post('/login',
               data={'username': 'user',
                     'password': 'user123'})
    
    # Try to delete another mod (this should fail)
    response = client.post(f'/mod/{mod_by_regular_user.id}/delete')
    assert response.status_code == HTTPStatus.FORBIDDEN
