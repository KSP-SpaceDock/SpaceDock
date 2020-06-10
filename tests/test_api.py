import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fixtures.client import client


@pytest.mark.usefixtures("client")
def test_api_browse(client: 'FlaskClient[Response]') -> None:
    resp = client.get('/api/browse')
    assert resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert resp.data == b'{"total":0,"count":30,"pages":1,"page":1,"result":[]}', 'Should be a simple empty db'
