"""API tests for game routes."""
import json


def test_games_list(client):
    """Test GET /api/game/all returns list of games."""
    response = client.get('/api/game/all')
    assert response.status_code == 200
    games = json.loads(response.data)
    assert isinstance(games, list)
    # Dev environment populates at least some games
    assert len(games) > 0
    # Check structure
    game = games[0]
    assert 'id' in game
    assert 'name' in game


def test_game_info(client):
    """Test GET /api/game/<game_id> returns game details."""
    # First get a game ID
    response = client.get('/api/game/all')
    games = json.loads(response.data)
    game_id = games[0]['id']

    response = client.get(f'/api/game/{game_id}')
    assert response.status_code == 200
    game = json.loads(response.data)
    assert game['id'] == game_id
    assert 'name' in game


def test_legacy_games_list(client):
    """Test legacy GET /api/games redirects to new route."""
    response = client.get('/api/games')
    assert response.status_code == 200
    games = json.loads(response.data)
    assert isinstance(games, list)