import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fixtures.client import client


@pytest.mark.usefixtures("client")
def test_bad_url(client: 'FlaskClient[Response]') -> None:
    # Arrange is handled by the fixture

    # Act
    bad_url_resp = client.get('/something_that_matches_no_routes/69/420')

    # Assert
    assert bad_url_resp.status_code == status.HTTP_404_NOT_FOUND, 'Request should fail'
    assert bad_url_resp.json is None, 'Should not be JSON'
    assert bad_url_resp.mimetype == 'text/html', 'Should be HTML'
    assert b'Not Found' in bad_url_resp.data, 'Should be a nice web page'
    assert b'Requested page not found. Looks like this was deleted, or maybe was never here.' in bad_url_resp.data, 'Tells us it\'s gone'


@pytest.mark.usefixtures("client")
def test_mod_not_found(client: 'FlaskClient[Response]') -> None:
    # Arrange is handled by the fixture

    # Act
    missing_mod_resp = client.get('/mod/20000')

    # Assert
    assert missing_mod_resp.status_code == status.HTTP_404_NOT_FOUND, 'Request should fail'
    assert missing_mod_resp.json is None, 'Should not be JSON'
    assert missing_mod_resp.mimetype == 'text/html', 'Should be HTML'
    assert b'Not Found' in missing_mod_resp.data, 'Should be a nice web page'
    assert b'Requested page not found. Looks like this was deleted, or maybe was never here.' in missing_mod_resp.data, 'Tells us it\'s gone'
