import random
from typing import TYPE_CHECKING

from .config import _cfgi

if TYPE_CHECKING:
    from wsgiref.types import StartResponse, WSGIEnvironment

def sampling_function(environ: "WSGIEnvironment") -> bool:
    # Don't bother profiling admin pages or static files
    if environ.get('PATH_INFO', '').startswith(("/admin", "/content", "/static")):
        return False
    max = _cfgi('requests-per-profile', 1)
    return random.randrange(0, max) == 0
