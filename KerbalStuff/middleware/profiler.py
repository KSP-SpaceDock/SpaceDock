from sys import stdout
import os
from os import access, W_OK
from time import time
from datetime import timedelta, datetime
from pstats import Stats
from cProfile import Profile
from typing import Optional, Iterable, Union, Callable, TextIO, List, TYPE_CHECKING, cast

from werkzeug.middleware.profiler import ProfilerMiddleware

if TYPE_CHECKING:
    from wsgiref.types import StartResponse, WSGIApplication, WSGIEnvironment


class ConditionalProfilerMiddleware(ProfilerMiddleware):
    def __init__(
        self,
        app: "WSGIApplication",
        stream: Optional[TextIO] = stdout,
        sort_by: Iterable[str] = ("time", "calls"),
        restrictions: Iterable[Union[str, int, float]] = (),
        profile_dir: Optional[str] = None,
        filename_format: str = "{method}.{path}.{elapsed:.0f}ms.{time:.0f}.prof",
        sampling_function: Optional[Callable[["WSGIEnvironment"], bool]] = None,
    ) -> None:
        super().__init__(app=app,
                         stream=stream, sort_by=sort_by, # type: ignore[arg-type]
                         restrictions=restrictions, profile_dir=profile_dir, filename_format=filename_format)
        self._app = app
        self._profile_dir = profile_dir
        self._sampling_function = sampling_function

    def __call__(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> List[bytes]:

        if (self._sampling_function and not self._sampling_function(environ)
            or self._profile_dir and not access(self._profile_dir, W_OK)):
            # Run without profiling
            response_body: List[bytes] = []
            app_iter = self._app(environ, start_response)
            response_body.extend(app_iter)
            if hasattr(app_iter, "close"):
                app_iter.close() # type: ignore[attr-defined]
            return [b"".join(response_body)]

        else:
            return super().__call__(environ, start_response)


class CherrypickingProfilerMiddleware(ProfilerMiddleware):
    def __init__(
        self,
        app: "WSGIApplication",
        stream: Optional[TextIO] = stdout,
        sort_by: Iterable[str] = ("time", "calls"),
        restrictions: Iterable[Union[str, int, float]] = (),
        profile_dir: Optional[str] = None,
        filename_format: str = "{method}.{path}.{elapsed:.0f}ms.{time:.0f}.prof",
        log_if_longer: Optional[timedelta] = None,
    ) -> None:
        super().__init__(app=app,
                         stream=stream, sort_by=sort_by, # type: ignore[arg-type]
                         restrictions=restrictions, profile_dir=profile_dir, filename_format=filename_format)
        self._app = app
        self._stream = stream
        self._sort_by = sort_by
        self._restrictions = restrictions
        self._profile_dir = profile_dir
        self._filename_format = filename_format
        self._log_if_longer = log_if_longer or timedelta(seconds=1)

    def __call__(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> List[bytes]:
        response_body: List[bytes] = []

        def catching_start_response(status, headers, exc_info=None):  # type: ignore
            start_response(status, headers, exc_info)
            return response_body.append

        def runapp() -> None:
            app_iter = self._app(environ,
                                 cast("StartResponse", catching_start_response))
            response_body.extend(app_iter)

            if hasattr(app_iter, "close"):
                app_iter.close()  # type: ignore

        profile = Profile()
        start = time()
        profile.runcall(runapp)
        body = b"".join(response_body)
        end = time()
        elapsed = end - start

        # Only save profiling data if slow
        if datetime.fromtimestamp(end) - datetime.fromtimestamp(start) >= self._log_if_longer:

            if self._profile_dir is not None:
                if callable(self._filename_format):
                    filename = self._filename_format(environ)
                else:
                    filename = self._filename_format.format(
                        method=environ["REQUEST_METHOD"],
                        path=environ["PATH_INFO"].strip("/").replace("/", ".") or "root",
                        elapsed=elapsed * 1000.0,
                        time=time(),
                    )
                filename = os.path.join(self._profile_dir, filename)
                profile.dump_stats(filename)

            if self._stream is not None:
                stats = Stats(profile, stream=self._stream)
                stats.sort_stats(*self._sort_by)
                print("-" * 80, file=self._stream)
                path_info = environ.get("PATH_INFO", "")
                print(f"PATH: {path_info!r}", file=self._stream)
                stats.print_stats(*self._restrictions)
                print(f"{'-' * 80}\n", file=self._stream)

        return [body]
