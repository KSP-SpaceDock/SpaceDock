"""Tests for SpaceDock/email.py."""
import pytest
from SpaceDock.email import send_confirmation, send_password_reset, send_password_changed
from SpaceDock.objects import User
from SpaceDock.database import db


def test_send_confirmation(flask_app):
    """Test sending confirmation email."""
    with flask_app.app_context():
        user = db.query(User).first()
        if not user:
            return
        
        # This will actually send an email through Celery
        send_confirmation(user)


def test_send_password_reset(flask_app):
    """Test sending password reset email."""
    with flask_app.app_context():
        user = db.query(User).first()
        if not user:
            return
        
        send_password_reset(user)


def test_send_password_changed(flask_app):
    """Test sending password changed email."""
    with flask_app.app_context():
        user = db.query(User).first()
        if not user:
            return
        
        send_password_changed(user)