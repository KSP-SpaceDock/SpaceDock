from datetime import datetime

import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fixtures.client import client
from KerbalStuff.objects import Publisher, Game, GameVersion, User, Mod, ModVersion
from KerbalStuff.database import db


@pytest.mark.usefixtures("client")
def test_api_mod(client: 'FlaskClient[Response]') -> None:
    # Arrange
    game = Game(
        name='Kerbal Space Program',
        publisher=Publisher(
            name='SQUAD',
        ),
        short='kerbal-space-program',
    )
    mod = Mod(
        name='Test Mod',
        short_description='A mod for testing',
        description='A mod that we will use to test the API',
        user=User(
            username='TestModAuthor',
            email='webmaster@spacedock.info',
        ),
        license='MIT',
        game=game,
        ckan=False,
        default_version=ModVersion(
            friendly_version="1.0.0.0",
            gameversion=GameVersion(
                friendly_version='1.2.3',
                game=game,
            ),
            download_path='/tmp/blah.zip',
            created=datetime.now(),
        ),
        published=True,
    )
    mod.default_version.mod = mod
    db.add(game)
    db.add(mod)
    db.commit()

    # Act
    resp = client.get('/api/mod/1')

    # Assert
    assert resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert resp.json['name'] == 'Test Mod', 'Name should match'
    assert resp.json['id'] == 1, 'ID number should match'
    assert resp.json['short_description'] == 'A mod for testing', 'Short description should match'
    assert resp.json['description'] == 'A mod that we will use to test the API', 'Short description should match'
    assert resp.json['author'] == 'TestModAuthor', 'Author should match'
    assert resp.json['license'] == 'MIT', 'License should match'
    assert resp.json['downloads'] == 0, 'Should have no downloads'
    assert resp.json['followers'] == 0, 'Should have no followers'
    assert resp.json['versions'][0]['friendly_version'] == '1.0.0.0', 'Version should match'
    assert resp.json['versions'][0]['game_version'] == '1.2.3', 'Version should match'


@pytest.mark.usefixtures("client")
def test_api_browse(client: 'FlaskClient[Response]') -> None:
    resp = client.get('/api/browse')
    assert resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert resp.data == b'{"total":0,"count":30,"pages":1,"page":1,"result":[]}', 'Should be a simple empty db'
