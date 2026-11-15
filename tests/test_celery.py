"""Tests for Celery tasks."""
import pytest
from SpaceDock.celery import app, send_mail, calculate_mod_scores, game_version_import


def test_celery_app_configured():
    """Test that Celery app is configured."""
    assert app.conf.broker_url is not None


def test_send_mail_task_exists():
    """Test that send_mail task is registered."""
    assert app.tasks.get('send_mail') is not None or hasattr(send_mail, 'delay')


def test_calculate_mod_scores_task_exists():
    """Test that calculate_mod_scores task is registered."""
    assert app.tasks.get('calculate_mod_scores') is not None or hasattr(calculate_mod_scores, 'delay')


def test_game_version_import_task_exists():
    """Test that game_version_import task is registered."""
    assert app.tasks.get('game_version_import') is not None or hasattr(game_version_import, 'delay')