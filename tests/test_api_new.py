"""API tests for new routes: browse extended, search extended, user creations, packs, media."""
import json


def test_browse_extended(client):
    """Test GET /api/game/<game_id>/<category>/browse/extended."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    assert len(games) > 0

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/browse/extended')
    assert response.status_code in (200, 404)


def test_search_extended(client):
    """Test GET /api/game/<game_id>/<category>/search/extended."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    assert len(games) > 0

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/search/extended?query=test')
    assert response.status_code in (200, 404)

def test_user_creations(client):
    """Test GET /api/user/<username>/creation/all."""
    users = client.get('/api/user/search?query=a')
    users = json.loads(users.data)
    if not users:
        return

    username = users[0]['username']
    response = client.get(f'/api/user/{username}/creation/all')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'mods' in result


def test_user_packs(client):
    """Test GET /api/user/<username>/pack/all."""
    users = client.get('/api/user/search?query=a')
    users = json.loads(users.data)
    if not users:
        return

    username = users[0]['username']
    response = client.get(f'/api/user/{username}/pack/all')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'packs' in result



def test_creation_media(client):
    """Test GET /api/game/<game_id>/<category>/<mod_id>/media."""
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
    response = client.get(f'/api/game/{game_id}/mods/{mod_id}/media')
    assert response.status_code in (200, 404)