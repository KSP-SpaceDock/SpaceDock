import json
import math
import urllib.parse
import os
import re
from functools import wraps
from typing import Union, List, Dict, Any, Optional, Callable, Tuple, Iterable

from flask import jsonify, redirect, request, Response, abort, session
from flask_login import current_user
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
import werkzeug.wrappers
from sqlalchemy.orm import Query

from .custom_json import CustomJSONEncoder
from .database import db, Base
from .objects import Game, Mod
from .search import search_mods

TRUE_STR = ('true', 'yes', 'on')
PARAGRAPH_PATTERN = re.compile('\n\n|\r\n\r\n')


def first_paragraphs(text: str) -> str:
    return '\n\n'.join(PARAGRAPH_PATTERN.split(text)[0:3])


def many_paragraphs(text:str) -> bool:
    return len(PARAGRAPH_PATTERN.split(text)) > 3


def dumb_object(model):  # type: ignore
    if type(model) is list:
        return [dumb_object(x) for x in model]

    result = {}

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        a = getattr(model, col.name)
        if not isinstance(a, Base):
            result[col.name] = a

    return result


def wrap_mod(mod: Mod) -> Optional[Dict[str, Any]]:
    details: Dict[str, Any] = dict()
    details['mod'] = mod
    if len(mod.versions) > 0:
        details['latest_version'] = mod.versions[0]
        details['safe_name'] = secure_filename(mod.name)[:64]
        details['details'] = '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64]
        details['dl_link'] = '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64] \
                             + '/download/' + mod.versions[0].friendly_version
    else:
        return None
    return details


def with_session(f: Callable[..., Any]) -> Callable[..., Any]:
    """Automatically commits to the database, and rolls back if the process throws an error.

    """
    @wraps(f)
    def go(*args: str, **kwargs: int) -> werkzeug.wrappers.Response:
        try:
            ret = f(*args, **kwargs)
            db.commit()
            return ret
        except:
            db.rollback()
            db.close()
            raise

    return go


def loginrequired(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: str, **kwargs: int) -> werkzeug.wrappers.Response:
        if not current_user or current_user.confirmation:
            return redirect("/login?return_to=" + urllib.parse.quote_plus(request.url))
        else:
            return f(*args, **kwargs)

    return wrapper


def adminrequired(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: str, **kwargs: int) -> werkzeug.wrappers.Response:
        if not current_user or current_user.confirmation:
            return redirect("/login?return_to=" + urllib.parse.quote_plus(request.url))
        else:
            if not current_user.admin:
                abort(403)
            return f(*args, **kwargs)

    return wrapper


def json_response(obj: Any, status: int = None) -> werkzeug.wrappers.Response:
    data = json.dumps(obj, cls=CustomJSONEncoder, separators=(',', ':'))
    return Response(data, status=status, mimetype='application/json')


def json_output(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: str, **kwargs: int) -> werkzeug.wrappers.Response:
        result = f(*args, **kwargs)
        if isinstance(result, tuple):
            return json_response(*result)
        if isinstance(result, (dict, list)):
            return json_response(result)
        # This is a fully fleshed out response, return it immediately
        return result

    return wrapper


def cors(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: str, **kwargs: int) -> Tuple[str, int]:
        res = f(*args, **kwargs)
        if request.headers.get('x-cors-status', False):
            if isinstance(res, tuple):
                json_text = res[0].data
                code = res[1]
            else:
                json_text = res.data
                code = 200
            o = json.loads(json_text)
            o['x-status'] = code
            return jsonify(o)
        return res

    return wrapper


def paginate_mods(mods: Query, page_size: int = 30) -> Tuple[List[Mod], int, int]:
    total_pages = math.ceil(mods.count() / page_size)
    page = get_page()
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1
    return mods.offset(page_size * (page - 1)).limit(page_size), page, total_pages


def get_page() -> int:
    try:
        return int(request.args.get('page', ''))
    except (ValueError, TypeError):
        return 1


def get_mods(ga: Game = None, query: str = '', page_size: int = 30) -> Tuple[Iterable[Mod], int, int]:
    page = get_page()
    mods, total_pages = search_mods(ga, query, page, page_size)
    return mods, page, total_pages


def get_game_info(**query: str) -> Game:
    if not query:
        query['short'] = 'kerbal-space-program'
    ga = Game.query.filter_by(**query).first()
    if not ga:
        abort(404)
    set_game_info(ga)
    return ga


def set_game_info(ga: Game) -> None:
    session['game'] = ga.id
    session['gamename'] = ga.name
    session['gameshort'] = ga.short
    session['gameid'] = ga.id


def check_mod_editable(mod: Mod, abort_response: Optional[Union[int, werkzeug.wrappers.Response]] = 403) -> bool:
    if current_user:
        if current_user.admin:
            return True
        if current_user.id == mod.user_id:
            return True
        if any(u.accepted and u.user == current_user for u in mod.shared_authors):
            return True
    if abort_response is not None:
        abort(abort_response)
    return False


def get_version_size(f: str) -> Optional[str]:
    if not os.path.isfile(f):
        return None

    size = os.path.getsize(f)
    if size < 1023:
        return "%d %s" % (size, ("byte" if size == 1 else "bytes"))
    elif size < 1048576:
        return "%3.2f KiB" % (size/1024)
    elif size < 1073741824:
        return "%3.2f MiB" % (size/1048576)
    elif size < 1099511627776:
        return "%3.2f GiB" % (size/1073741824)
    else:
        return "%3.2f TiB" % (size/1099511627776)


def jsonify_exception(e: Exception) -> werkzeug.wrappers.Response:
    if isinstance(e, HTTPException):
        # Start with the correct headers and status code from the error
        response = e.get_response()
        # Replace the body with JSON
        response.mimetype = 'application/json'
        response.data = json.dumps({
            "error": True,
            "reason": f'{e.code} {e.name}: {e.description}',
            "code": e.code,
        }, cls=CustomJSONEncoder, separators=(',', ':'))
        return response
    else:
        return json_response({
            "error": True,
            "code": 500,
            "reason": f'500 Internal Server Error: {str(e)}',
        }, 500)
