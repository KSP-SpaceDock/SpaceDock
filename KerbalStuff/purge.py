from socket import socket
from typing import Union, Tuple

import threading
import dns.resolver
import requests
from urllib3.util import connection

from .config import _cfg

_orig_create_connection = connection.create_connection
_create_connection_mutex = threading.Lock()


def purge_download(download_path: str) -> None:
    protocol = _cfg('protocol')
    cdn_domain = _cfg('cdn-domain')
    if protocol and cdn_domain:
        global _create_connection_mutex
        # Only one thread is allowed to mess with connection.create_connection at a time
        with _create_connection_mutex:
            connection.create_connection = create_connection_cdn_purge  # type: ignore[assignment]
            try:
                requests.request('PURGE',
                                 protocol + '://' + cdn_domain + '/' + download_path)
            except requests.exceptions.RequestException:
                pass
            global _orig_create_connection
            connection.create_connection = _orig_create_connection


def create_connection_cdn_purge(address: Tuple[str, int],
                                *args: str,
                                **kwargs: int) -> socket:
    # Taken from https://stackoverflow.com/a/22614367
    host, port = address

    cdn_internal = _cfg('cdn-internal')
    cdn_domain = _cfg('cdn-domain')
    if cdn_internal and cdn_domain and cdn_domain.startswith(host):
        result = dns.resolver.resolve(cdn_internal)
        host = result[0].to_text()

    global _orig_create_connection
    assert callable(_orig_create_connection)
    return _orig_create_connection((host, port), *args, **kwargs)  # type: ignore[arg-type]
