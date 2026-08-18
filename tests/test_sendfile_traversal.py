import os
from http import HTTPStatus

import pytest
from werkzeug.exceptions import NotFound

from .fixtures.fake_config import dummy  # noqa: F401
from KerbalStuff.config import config, env
from KerbalStuff.app import app
from KerbalStuff.common import sendfile


@pytest.fixture
def storage(tmp_path):  # type: ignore[no-untyped-def]
    """A storage folder with one file in it, and a secret next to it."""
    root = tmp_path / 'storage'
    root.mkdir()
    (root / 'legit.txt').write_text('a real upload')
    (tmp_path / 'config.ini').write_text('secret-key=super-secret')

    previous = config[env].get('storage')
    config[env]['storage'] = str(root)
    config[env]['use-x-accel'] = 'false'
    yield root
    if previous is None:
        del config[env]['storage']
    else:
        config[env]['storage'] = previous


@pytest.mark.usefixtures("storage")
@pytest.mark.parametrize('path', [
    '../config.ini',
    '../../etc/passwd',
    'sub/../../config.ini',
    os.path.join('..', 'config.ini'),
])
def test_sendfile_rejects_traversal(storage, path: str) -> None:  # type: ignore[no-untyped-def]
    """Paths pointing outside the storage folder should 404.

    ModList.background used to be settable from the pack edit form, which made
    /pack/<id>/<name>/background serve any file on disk.
    """
    with app.test_request_context():
        with pytest.raises(NotFound):
            sendfile(path)


@pytest.mark.usefixtures("storage")
def test_sendfile_serves_contained_path(storage) -> None:  # type: ignore[no-untyped-def]
    """Normal files still work."""
    with app.test_request_context():
        response = sendfile('legit.txt')
        assert response.status_code == HTTPStatus.OK
        # send_file streams, turn that off so we can read the body
        response.direct_passthrough = False
        assert b'a real upload' in response.get_data()
