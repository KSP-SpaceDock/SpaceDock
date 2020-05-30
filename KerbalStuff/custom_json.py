from datetime import datetime, timezone
from typing import Any

from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.astimezone(timezone.utc).isoformat()
        try:
            return list(obj)
        except TypeError:
            pass
        return super().default(obj)
