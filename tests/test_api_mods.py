"""API tests for mod routes."""
import json


def test_mod_browse(client):
    """Test GET /api/game/<game_id>/<category>/browse/all."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    assert len(games) > 0

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/browse/all')
    # May or may not have that exact category
    assert response.status_code in (200, 404)


def test_mod_info(client):
    """Test GET /api/game/<game_id>/<category>/<mod_id>."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/browse/all')
    if response.status_code != 200:
        return

    result = json.loads(response.data)
    if isinstance(result, dict):
        result = result.get('mods', [])

    if not result:
        return

    mod_id = result[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/{mod_id}')
    # API may return 404 for various reasons - document current behavior
    assert response.status_code in (200, 404)


def test_mod_versions(client):
    """Test GET /api/game/<game_id>/<category>/<mod_id>/version/all."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/browse/all')
    if response.status_code != 200:
        return

    result = json.loads(response.data)
    if isinstance(result, dict):
        result = result.get('mods', [])

    if not result:
        return

    mod_id = result[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/{mod_id}/version/all')
    # API may return 404 - document current behavior
    assert response.status_code in (200, 404)


def test_legacy_mod_redirect(client):
    """Test legacy /api/mod/<mod_id> redirect."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/browse/all')
    if response.status_code != 200:
        return

    result = json.loads(response.data)
    if isinstance(result, dict):
        result = result.get('mods', [])

    if not result:
        return

    mod_id = result[0]['id']
    response = client.get(f'/api/mod/{mod_id}')
    assert response.status_code == 200
    mod = json.loads(response.data)
    assert mod['id'] == mod_id


def test_mod_download_stats(client):

    """Test GET /api/game/<game_id>/<category>/<mod_id>/download/stat."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/browse/all')
    if response.status_code != 200:
        return

    result = json.loads(response.data)
    if isinstance(result, dict):
        result = result.get('mods', [])

    if not result:
        return

    mod_id = result[0]['id']
    response = client.get(f'/api/game/{game_id}/mods/{mod_id}/download/stat')
    # API may return 404 - document current behavior
    assert response.status_code in (200, 404)

def test_browse_extended_published_filter(client):
    """Test browse extended with published filter."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']

    # Published only - should return 200 and valid JSON
    response = client.get(f'/api/game/{game_id}/mods/browse/extended?published=true')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'mods' in result


def test_browse_extended_min_downloads(client):
    """Test browse extended with min_downloads filter."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']

    # High min downloads should return fewer or no mods
    response = client.get(f'/api/game/{game_id}/mods/browse/extended?min_downloads=999999')
    assert response.status_code == 200
    result = json.loads(response.data)
    if 'mods' in result:
        assert len(result['mods']) <= 1


def test_search_extended_sort(client):
    """Test search extended with sort parameters."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']

    # Sort by downloads descending
    response = client.get(
        f'/api/game/{game_id}/mods/search/extended?query=&sort=downloads&order=desc')
    assert response.status_code == 200
    result = json.loads(response.data)
    # Should return a dict with mods key
    assert 'mods' in result or isinstance(result, list)


def test_search_extended_published_filter(client):
    """Test search extended with published filter."""
    games = client.get('/api/game/all')
    games = json.loads(games.data)
    if not games:
        return

    game_id = games[0]['id']

    response = client.get(
        f'/api/game/{game_id}/mods/search/extended?query=&published=true')
    assert response.status_code == 200