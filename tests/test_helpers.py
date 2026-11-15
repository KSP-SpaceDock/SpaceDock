"""Tests for SpaceDock/helpers.py."""
from SpaceDock.helpers import is_admin, following_mod
from SpaceDock.objects import User, Mod
from SpaceDock.database import db


def test_is_admin_not_logged_in(client, flask_app):
    """Test is_admin when not logged in."""
    with flask_app.app_context():
        assert is_admin() is False


def test_is_admin_regular_user(client, flask_app):
    """Test is_admin for regular user."""
    with flask_app.app_context():
        user = db.query(User).filter(User.username == "user").first()
        if not user:
            return
        
        # Login as regular user
        client.post("/login", data={
            "username": user.username,
            "password": "development"
        }, follow_redirects=True)
        
        assert is_admin() is False
        client.post("/logout", follow_redirects=True)


def test_is_admin_admin_user(client, flask_app):
    """Test admin user has admin flag."""
    with flask_app.app_context():
        admin = db.query(User).filter(User.username == "admin").first()
        assert admin is not None
        assert admin.admin is True


def test_following_mod_not_logged_in(client, flask_app):
    """Test following_mod when not logged in."""
    with flask_app.app_context():
        mod = db.query(Mod).first()
        if not mod:
            return
        assert following_mod(mod) is False


def test_following_mod_regular_user(client, flask_app):
    """Test following_mod for regular user."""
    with flask_app.app_context():
        user = db.query(User).filter(User.username == "user").first()
        if not user:
            return
        
        mod = db.query(Mod).first()
        if not mod:
            return
        
        # Login as regular user
        client.post("/login", data={
            "username": user.username,
            "password": "development"
        }, follow_redirects=True)
        
        result = following_mod(mod)
        assert isinstance(result, bool)
        
        client.post("/logout", follow_redirects=True)