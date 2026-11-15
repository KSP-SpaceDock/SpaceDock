"""Tests for SpaceDock/notification.py."""
import pytest
from SpaceDock.notification import send_add_notifications, send_change_notifications
from SpaceDock.objects import Mod, Notification
from SpaceDock.database import db


def test_send_add_notifications(flask_app):
    """Test sending add notifications."""
    with flask_app.app_context():
        mod = db.query(Mod).first()
        if not mod:
            return
        
        send_add_notifications(mod)


def test_send_change_notifications(flask_app):
    """Test sending change notifications."""
    with flask_app.app_context():
        mod = db.query(Mod).first()
        if not mod:
            return
        
        send_change_notifications(mod, "update", force=True)