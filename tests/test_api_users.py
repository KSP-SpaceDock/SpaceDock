"""API tests for user routes."""
import json


def test_user_info(client):
    """Test GET /api/user/<username>."""
    # Dev environment creates admin and user users
    response = client.get('/api/user/admin')
    assert response.status_code == 200
    user = json.loads(response.data)
    assert user['username'] == 'admin'


def test_search_user(client):
    """Test GET /api/user/search."""
    response = client.get('/api/user/search?query=admin')
    assert response.status_code == 200
    users = json.loads(response.data)
    assert isinstance(users, list)
    # Should find admin user
    found = [u for u in users if u['username'] == 'admin']
    assert len(found) > 0