from datetime import datetime

import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fixtures.client import client
from KerbalStuff.objects import Publisher, Game, GameVersion, User, Mod, ModVersion
from KerbalStuff.database import db


@pytest.mark.usefixtures("client")
def test_api_browse(client: 'FlaskClient[Response]') -> None:
    # Arrange is handled by the fixture

    # Act
    browse_resp = client.get('/api/browse')
    new_resp = client.get('/api/browse/new')
    top_resp = client.get('/api/browse/top')
    featured_resp = client.get('/api/browse/featured')

    # Assert
    assert browse_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert browse_resp.data == b'{"total":0,"count":30,"pages":1,"page":1,"result":[]}', 'Should be a simple empty db'

    assert new_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert new_resp.data == b'[]', 'Should return empty list'

    assert top_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert top_resp.data == b'[]', 'Should return empty list'

    assert featured_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert featured_resp.data == b'[]', 'Should return empty list'
