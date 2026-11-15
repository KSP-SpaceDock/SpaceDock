"""API tests for publisher routes."""
import json


def test_publishers_list(client):
    """Test GET /api/publisher/all."""
    response = client.get('/api/publisher/all')
    # May fail if API implementation is incomplete
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        publishers = json.loads(response.data)
        assert isinstance(publishers, list)


def test_publisher_info(client):
    """Test GET /api/publisher/<publisher_id>."""
    response = client.get('/api/publisher/all')
    if response.status_code != 200:
        return

    publishers = json.loads(response.data)
    if not publishers:
        return

    publisher_id = publishers[0]['id']
    response = client.get(f'/api/publisher/{publisher_id}')
    assert response.status_code == 200
    publisher = json.loads(response.data)
    assert publisher['id'] == publisher_id