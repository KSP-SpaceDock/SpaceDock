from datetime import datetime, timezone

from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.astimezone(timezone.utc).isoformat()
        try:
            return list(obj)
        except TypeError:
            pass
        return super().default(obj)
