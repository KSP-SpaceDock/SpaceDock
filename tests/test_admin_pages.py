"""Tests for admin blueprint pages."""
import pytest
from SpaceDock.objects import User
from SpaceDock.database import db


def test_admin_main_redirects(client, flask_app):
    """Test admin main page redirects."""
    with flask_app.app_context():
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            return
        
        client.post("/login", data={
            "username": admin.username,
            "password": "development"
        }, follow_redirects=True)
        
        response = client.get("/admin")
        assert response.status_code in (200, 302)
        
        client.post("/logout", follow_redirects=True)


def test_admin_users_page(client, flask_app):
    """Test admin users list page."""
    with flask_app.app_context():
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            return
        
        client.post("/login", data={
            "username": admin.username,
            "password": "development"
        }, follow_redirects=True)
        
        response = client.get("/admin/users/1")
        assert response.status_code == 200
        
        client.post("/logout", follow_redirects=True)


def test_admin_games_page(client, flask_app):
    """Test admin games list page."""
    with flask_app.app_context():
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            return
        
        client.post("/login", data={
            "username": admin.username,
            "password": "development"
        }, follow_redirects=True)
        
        response = client.get("/admin/games/1")
        assert response.status_code == 200
        
        client.post("/logout", follow_redirects=True)


def test_admin_publishers_page(client, flask_app):
    """Test admin publishers list page."""
    with flask_app.app_context():
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            return
        
        client.post("/login", data={
            "username": admin.username,
            "password": "development"
        }, follow_redirects=True)
        
        response = client.get("/admin/publishers/1")
        assert response.status_code == 200
        
        client.post("/logout", follow_redirects=True)