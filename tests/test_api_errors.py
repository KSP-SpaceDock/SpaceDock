import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fixtures.client import client


@pytest.mark.usefixtures("client")
def test_api_bad_url(client: 'FlaskClient[Response]') -> None:
    # Arrange is handled by the fixture

    # Act
    bad_url_resp = client.get('/api/something_that_matches_no_routes/69/420')

    # Assert
    assert bad_url_resp.status_code == status.HTTP_404_NOT_FOUND, 'Request should fail'
    assert bad_url_resp.json['code'] == status.HTTP_404_NOT_FOUND, 'Code should match'
    assert bad_url_resp.json['error'] == True, 'Should contain "error" property'
    assert 'not found' in bad_url_resp.json['reason'], 'Reason should be typical 404 lingo'


@pytest.mark.usefixtures("client")
def test_api_mod_not_found(client: 'FlaskClient[Response]') -> None:
    # Arrange is handled by the fixture

    # Act
    missing_mod_resp = client.get('/api/mod/20000')

    # Assert
    assert missing_mod_resp.status_code == status.HTTP_404_NOT_FOUND, 'Request should fail'
    assert missing_mod_resp.json['error'] == True, 'Should contain "error" property'
    assert missing_mod_resp.json['reason'] == 'Mod not found.', 'Reason should match'
