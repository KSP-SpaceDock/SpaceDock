from datetime import datetime
from typing import Any

from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        try:
            return list(obj)
        except TypeError:
            pass
        return super().default(obj)
