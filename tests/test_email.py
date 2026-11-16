"""Tests for SpaceDock/email.py."""
import pytest
from unittest.mock import patch, MagicMock
from SpaceDock.email import send_confirmation, send_password_reset, send_password_changed
from SpaceDock.objects import User
from SpaceDock.database import db


@patch('SpaceDock.email.send_mail')
def test_send_confirmation(mock_send_mail):
    """Test sending confirmation email."""
    mock_send_mail.delay = MagicMock()
    mock_user = MagicMock()
    mock_user.confirmation = "test-confirm-token"
    mock_user.email = "test@example.test"
    send_confirmation(mock_user)
    mock_send_mail.delay.assert_called_once()


@patch('SpaceDock.email.send_mail')
def test_send_password_reset(mock_send_mail):
    """Test sending password reset email."""
    mock_send_mail.delay = MagicMock()
    mock_user = MagicMock()
    mock_user.email = "test@example.test"
    send_password_reset(mock_user)
    mock_send_mail.delay.assert_called_once()


@patch('SpaceDock.email.send_mail')
def test_send_password_changed(mock_send_mail):
    """Test sending password changed email."""
    mock_send_mail.delay = MagicMock()
    mock_user = MagicMock()
    mock_user.email = "test@example.test"
    send_password_changed(mock_user)
    mock_send_mail.delay.assert_called_once()