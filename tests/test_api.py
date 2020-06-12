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
            description='Test author of a test mod',
            email='webmaster@spacedock.info',
            forumUsername='TestForumUser',
            public=True,
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
    publishers_resp = client.get('/api/publishers')
    games_resp = client.get('/api/games')
    kspversions_resp = client.get('/api/kspversions')
    gameversions_resp = client.get('/api/1/versions')
    mod_resp = client.get('/api/mod/1')
    mod_version_resp = client.get('/api/mod/1/latest')
    user_resp = client.get('/api/user/TestModAuthor')

    # Assert
    assert mod_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert mod_resp.json['name'] == 'Test Mod', 'Name should match'
    assert mod_resp.json['id'] == 1, 'ID number should match'
    assert mod_resp.json['short_description'] == 'A mod for testing', 'Short description should match'
    assert mod_resp.json['description'] == 'A mod that we will use to test the API', 'Short description should match'
    assert mod_resp.json['author'] == 'TestModAuthor', 'Author should match'
    assert mod_resp.json['license'] == 'MIT', 'License should match'
    assert mod_resp.json['downloads'] == 0, 'Should have no downloads'
    assert mod_resp.json['followers'] == 0, 'Should have no followers'
    assert mod_resp.json['versions'][0]['friendly_version'] == '1.0.0.0', 'Version should match'
    assert mod_resp.json['versions'][0]['game_version'] == '1.2.3', 'Game version should match'

    assert kspversions_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert kspversions_resp.json[0]['id'] == 1, 'Game version id should match'
    assert kspversions_resp.json[0]['friendly_version'] == '1.2.3', 'Game version should match'

    assert gameversions_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert gameversions_resp.json[0]['id'] == 1, 'Game version id should match'
    assert gameversions_resp.json[0]['friendly_version'] == '1.2.3', 'Game version should match'

    assert games_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert games_resp.json[0]['id'] == 1, 'Game id should match'
    assert games_resp.json[0]['name'] == 'Kerbal Space Program', 'Game name should match'

    assert publishers_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert publishers_resp.json[0]['id'] == 1, 'Publisher id should match'
    assert publishers_resp.json[0]['name'] == 'SQUAD', 'Publisher name should match'

    assert mod_version_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert mod_version_resp.json['friendly_version'] == '1.0.0.0', 'Version should match'
    assert mod_version_resp.json['game_version'] == '1.2.3', 'Game version should match'
    assert mod_version_resp.json['download_path'] == '/mod/1/Test%20Mod/download/1.0.0.0', 'Download should match'

    assert user_resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert user_resp.json['username'] == 'TestModAuthor', 'Username should match'
    assert user_resp.json['description'] == 'Test author of a test mod', 'Description should match'
    assert user_resp.json['forumUsername'] == 'TestForumUser', 'Forum name should match'
    assert user_resp.json['mods'][0]['name'] == 'Test Mod', 'Mod should be returned'


@pytest.mark.usefixtures("client")
def test_api_browse(client: 'FlaskClient[Response]') -> None:
    resp = client.get('/api/browse')
    assert resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert resp.data == b'{"total":0,"count":30,"pages":1,"page":1,"result":[]}', 'Should be a simple empty db'
