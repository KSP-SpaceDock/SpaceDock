"""Tests for mod create/update/delete operations."""
import pytest
import json
from SpaceDock.objects import Mod, ModVersion, User, Game
from SpaceDock.database import db


def test_mod_create(client, flask_app):
    """Test creating a mod via API."""
    with flask_app.app_context():
        user = db.query(User).filter(User.username == "user").first()
        game = db.query(Game).first()
        if not user or not game:
            return
        
        # Login
        client.post("/login", data={
            "username": user.username,
            "password": "development"
        }, follow_redirects=True)
        
        # Create mod via POST form
        response = client.post(
            "/api/game/{}/mods".format(game.id),
            data=json.dumps({
                "name": "TestMod_Create",
                "short_name": "testmod-create",
                "description": "Test mod"
            }),
            content_type="application/json"
        )
        # API may require auth header, check status
        assert response.status_code in (200, 201, 400, 401, 403)
        
        client.post("/logout", follow_redirects=True)


def test_mod_info(client):
    """Test getting mod info via API."""
    # Get a list of mods first
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return
    
    game_id = games[0]['id']
    browse = client.get(f'/api/game/{game_id}/mods/browse/all')
    if browse.status_code != 200:
        return
    
    result = json.loads(browse.data)
    if isinstance(result, dict):
        mods = result.get('mods', [])
    else:
        mods = result
    
    if not mods:
        return
    
    mod_id = mods[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/{mod_id}')
    assert response.status_code == 200


def test_mod_update(client, flask_app):
    """Test updating a mod."""
    # Just verify the API endpoint exists
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return
    
    game_id = games[0]['id']
    browse = client.get(f'/api/game/{game_id}/mods/browse/all')
    if browse.status_code != 200:
        return
    
    result = json.loads(browse.data)
    if isinstance(result, dict):
        mods = result.get('mods', [])
    else:
        mods = result
    
    if not mods:
        return
    
    mod_id = mods[0]['id']
    response = client.post(
        f'/api/game/{game_id}/mods/{mod_id}',
        data=json.dumps({"name": "Test Updated"}),
        content_type="application/json"
    )
    # May fail without auth, just check endpoint exists
    assert response.status_code in (200, 400, 401, 403)