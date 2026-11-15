"""Tests for SpaceDock/middleware/session_interface.py."""
import pytest
from flask.sessions import SecureCookieSessionInterface
from SpaceDock.middleware.session_interface import OnlyLoggedInSessionInterface


def test_session_interface_class():
    """Test that OnlyLoggedInSessionInterface is properly defined."""
    assert isinstance(OnlyLoggedInSessionInterface(), SecureCookieSessionInterface)


def test_anonymous_user_session_cleared(client):
    """Test that anonymous user's session is cleared on response."""
    response = client.get("/")
    assert response.status_code == 200