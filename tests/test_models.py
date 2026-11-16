"""Tests for database models CRUD operations."""
import pytest
from SpaceDock.objects import (
    User, Mod, ModVersion, Game, GameVersion, Publisher,
    ModList, ModListItem, Featured, BlogPost, Following,
    DownloadEvent, FollowEvent, ReferralEvent, Media
)
from SpaceDock.database import db


def test_user_crud(flask_app):
    """Test User model CRUD."""
    with flask_app.app_context():
        # Create
        user = User(username="testuser_crud", email="test_crud@example.test")
        user.set_password("password")
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None
        
        # Read
        found = db.query(User).filter(User.username == "testuser_crud").first()
        assert found is not None
        assert found.email == "test_crud@example.test"
        
        # Update
        found.email = "updated@example.test"
        db.commit()
        db.refresh(found)
        assert found.email == "updated@example.test"
        
        # Delete
        db.delete(found)
        db.commit()
        
        # Verify deleted
        deleted = db.query(User).filter(User.username == "testuser_crud").first()
        assert deleted is None


def test_mod_crud(flask_app):
    """Test Mod model CRUD."""
    with flask_app.app_context():
        # Get existing user and game
        user = db.query(User).first()
        game = db.query(Game).first()
        if not user or not game:
            return
        
        mod = Mod(name="TestMod_CRUD", user_id=user.id, game_id=game.id)
        mod.description = "Test mod description"
        mod.short_description = "Short test description"
        db.add(mod)
        db.commit()
        db.refresh(mod)
        
        # Read
        found = db.query(Mod).filter(Mod.name == "TestMod_CRUD").first()
        assert found is not None
        
        # Update
        found.name = "TestMod_CRUD_Updated"
        db.commit()
        db.refresh(found)
        assert found.name == "TestMod_CRUD_Updated"
        
        # Delete
        db.delete(found)
        db.commit()


def test_mod_version_crud(flask_app):
    """Test ModVersion model CRUD."""
    with flask_app.app_context():
        mod = db.query(Mod).first()
        if not mod:
            return
        
        # Create
        version = ModVersion(
            mod_id=mod.id,
            friendly_version="99.0.0-test",
            download_path="test/modversion_crud.zip",
            download_size=1024
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        assert version.id is not None
        
        # Read
        found = db.query(ModVersion).filter(ModVersion.friendly_version == "99.0.0-test").first()
        assert found is not None
        
        # Update
        found.download_size = 2048
        db.commit()
        db.refresh(found)
        assert found.download_size == 2048
        
        # Delete
        db.delete(found)
        db.commit()


def test_game_crud(flask_app):
    """Test Game model CRUD."""
    with flask_app.app_context():
        publisher = db.query(Publisher).first()
        if not publisher:
            return
        
        # Create
        game = Game(name="TestGame_CRUD", publisher_id=publisher.id)
        game.active = True
        db.add(game)
        db.commit()
        db.refresh(game)
        assert game.id is not None
        
        # Read
        found = db.query(Game).filter(Game.name == "TestGame_CRUD").first()
        assert found is not None
        
        # Update
        found.name = "TestGame_CRUD_Updated"
        db.commit()
        db.refresh(found)
        assert found.name == "TestGame_CRUD_Updated"
        
        # Delete
        db.delete(found)
        db.commit()


def test_publisher_crud(flask_app):
    """Test Publisher model CRUD."""
    with flask_app.app_context():
        # Create
        publisher = Publisher(name="TestPublisher_CRUD")
        db.add(publisher)
        db.commit()
        db.refresh(publisher)
        assert publisher.id is not None
        
        # Read
        found = db.query(Publisher).filter(Publisher.name == "TestPublisher_CRUD").first()
        assert found is not None
        
        # Update
        found.name = "TestPublisher_CRUD_Updated"
        db.commit()
        db.refresh(found)
        assert found.name == "TestPublisher_CRUD_Updated"
        
        # Delete
        db.delete(found)
        db.commit()