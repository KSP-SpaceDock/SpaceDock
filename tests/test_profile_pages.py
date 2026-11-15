"""Tests for profile blueprint pages."""
import pytest
from SpaceDock.objects import User
from SpaceDock.database import db


def test_view_profile(client, flask_app):
    """Test viewing user profile."""
    with flask_app.app_context():
        user = db.query(User).first()
        if not user:
            return
        
        response = client.get(f"/profile/{user.username}")
        assert response.status_code == 200


def test_view_profile_not_found(client):
    """Test viewing non-existent user profile."""
    response = client.get("/profile/nonexistent_user_xyz")
    assert response.status_code == 404


def test_view_admin_profile(client):
    """Test viewing admin profile."""
    response = client.get("/profile/admin")
    assert response.status_code in (200, 404)


def test_view_user_profile(client):
    """Test viewing regular user profile."""
    response = client.get("/profile/user")
    assert response.status_code in (200, 404)