from sys import stdout
from typing import Optional, Iterable, Union, Callable, TextIO, List, TYPE_CHECKING

from werkzeug.contrib.profiler import ProfilerMiddleware

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
        self._sampling_function = sampling_function

    def __call__(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> List[bytes]:

        if self._sampling_function and not self._sampling_function(environ):
            # Run without profiling
            response_body: List[bytes] = []
            app_iter = self._app(environ, start_response)
            response_body.extend(app_iter)
            if hasattr(app_iter, "close"):
                app_iter.close() # type: ignore[attr-defined]
            return [b"".join(response_body)]

        else:
            return super().__call__(environ, start_response)
