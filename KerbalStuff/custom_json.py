from datetime import datetime, timezone
from typing import Any

from json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.astimezone(timezone.utc).isoformat()
        try:
            return list(o)
        except TypeError:
            pass
        return super().default(o)
