"""
Backend model tests for SpaceDock.

This file contains unit tests for database models.
"""

import pytest
from KerbalStuff.objects import User, Mod, Game, Publisher, GameVersion, ModVersion
from KerbalStuff.database import db


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    return user


@pytest.fixture
def sample_game():
    """Create a sample game for testing."""
    publisher = Publisher(name="Test Publisher")
    game = Game(
        name="Test Game",
        publisher=publisher,
        short="test-game",
        active=True,
    )
    return game


@pytest.fixture
def sample_mod(sample_user, sample_game):
    """Create a sample mod for testing."""
    game_version = GameVersion(friendly_version="1.0.0", game=sample_game)
    mod_version = ModVersion(
        friendly_version="1.0.0",
        gameversion=game_version,
        download_path="/tmp/test.zip",
    )
    mod = Mod(
        name="Test Mod",
        short_description="A test mod",
        description="This is a test mod for testing purposes.",
        user=sample_user,
        license="MIT",
        game=sample_game,
        default_version=mod_version,
    )
    mod_version.mod = mod
    return mod


def test_user_creation(sample_user):
    """Test user creation and password hashing."""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    assert sample_user.check_password("password123") is True
    assert sample_user.check_password("wrongpassword") is False


def test_mod_creation(sample_mod):
    """Test mod creation and relationships."""
    assert sample_mod.name == "Test Mod"
    assert sample_mod.short_description == "A test mod"
    assert sample_mod.license == "MIT"
    assert sample_mod.game.name == "Test Game"
    assert sample_mod.user.username == "testuser"
    assert sample_mod.default_version.friendly_version == "1.0.0"


def test_game_creation(sample_game):
    """Test game creation and relationships."""
    assert sample_game.name == "Test Game"
    assert sample_game.short == "test-game"
    assert sample_game.active is True
    assert sample_game.publisher.name == "Test Publisher"


def test_mod_version_relationship(sample_mod):
    """Test mod version relationships."""
    assert sample_mod.default_version.mod == sample_mod
    assert sample_mod.default_version.gameversion.game == sample_mod.game
