"""Tests for SpaceDock/search.py."""
import pytest
from SpaceDock.search import get_mod_score, versions_behind, apply_search_to_query, search_mods
from SpaceDock.objects import Mod, ModVersion, Game, GameVersion, User
from SpaceDock.database import db


def test_get_mod_score(flask_app):
    """Test mod scoring algorithm."""
    with flask_app.app_context():
        mod = db.query(Mod).first()
        if not mod:
            return  # No mods in database
        
        score = get_mod_score(mod)
        assert isinstance(score, int)


def test_versions_behind(flask_app):
    """Test game version tracking."""
    with flask_app.app_context():
        # Find a mod that has a default version
        from sqlalchemy import exists
        mod = db.query(Mod).filter(Mod.default_version_id != None).first()
        if not mod:
            return
        
        behind = versions_behind(mod)
        assert isinstance(behind, int)
        assert behind >= 0


def test_apply_search_to_query_basic(flask_app):
    """Test basic text search."""
    with flask_app.app_context():
        mods = db.query(Mod).first()
        if not mods:
            return
        
        query = db.query(Mod)
        # Search for something that should match
        filtered = apply_search_to_query(query, "test")
        results = filtered.all()
        assert isinstance(results, list)


def test_apply_search_to_query_negative(flask_app):
    """Test negative search terms."""
    with flask_app.app_context():
        query = db.query(Mod)
        filtered = apply_search_to_query(query, "-test")
        results = filtered.all()
        assert isinstance(results, list)


def test_search_mods(flask_app):
    """Test mod search functionality."""
    with flask_app.app_context():
        games = db.query(Game).all()
        if not games:
            return
        
        game_id = games[0].id
        mods, total_pages = search_mods(game_id, "test", 0, 10)
        assert isinstance(mods, list)
        assert isinstance(total_pages, int)
        assert total_pages >= 0


def test_search_users(flask_app):
    """Test user search."""
    from SpaceDock.search import search_users
    
    with flask_app.app_context():
        users = search_users("a", 0)
        assert isinstance(users, list)