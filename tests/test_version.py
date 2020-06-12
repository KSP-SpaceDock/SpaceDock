import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fixtures.client import client


@pytest.mark.usefixtures("client")
def test_version(client: 'FlaskClient[Response]') -> None:
    # Arrange is handled by the fixture

    # Act
    resp = client.get('/version')

    # Assert
    assert resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert resp.data.startswith(b'commit'), 'Response should start with "commit"'
    assert b'\nAuthor: ' in resp.data, 'Response should return a Author header'
    assert b'\nDate: ' in resp.data, 'Response should return a Date header'
