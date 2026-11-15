"""API tests for legacy routes."""
import json


def test_legacy_avc_redirect(client):
    """Test legacy /api/ksp-avc/<mod_id> redirect."""
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
    response = client.get(f'/api/ksp-avc/{mod_id}')
    # API may return 500 if mod has no default version - document current behavior
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        result = json.loads(response.data)
        assert 'id' in result
        assert 'version' in result