import math
from typing import Union, List, Tuple, Dict, Any
import datetime
from datetime import timezone
from pathlib import Path
from subprocess import run, PIPE

from flask import Blueprint, render_template, redirect, request, abort, url_for
from flask_login import login_user, current_user
from sqlalchemy import desc, or_, func
from sqlalchemy.orm import Query
import werkzeug.wrappers

from ..common import adminrequired, with_session, TRUE_STR
from ..config import _cfg
from ..database import db
from ..email import send_bulk_email
from ..objects import Mod, GameVersion, Game, Publisher, User

admin = Blueprint('admin', __name__, template_folder='../../templates/admin')
ITEMS_PER_PAGE = 10


@admin.route("/admin")
@adminrequired
def admin_main() -> werkzeug.wrappers.Response:
    return redirect(url_for('admin.profiling', page=1))


@admin.route("/admin/profiling/<int:page>")
@adminrequired
def profiling(page: int) -> Union[str, werkzeug.wrappers.Response]:
    if page < 1:
        return redirect(url_for('admin.profiling', page=1, **request.args))
    prof_dir = _cfg('profile-dir')
    profilings = [] if not prof_dir else list(map(
        parse_prof_filename,
        sorted(Path(prof_dir).glob('*.prof'),
               key=lambda p: -p.stat().st_mtime)))
    query = request.args.get('query', type=str)
    if query:
        terms = query.split(' ')
        profilings = [p for p in profilings
                      if all(map(lambda t: query_term_matches(t, p), terms))]
    total_pages = max(1, math.ceil(len(profilings) / ITEMS_PER_PAGE))
    profilings = profilings[(page - 1) * ITEMS_PER_PAGE : page * ITEMS_PER_PAGE]
    return render_template("admin-profiling.html",
                           profilings=profilings, query=query,
                           page=page, total_pages=total_pages)


def parse_prof_filename(p: Path) -> Dict[str, Any]:
    pieces = p.name.split('.')
    route_pieces = pieces[1:-3]
    # ProfilerMiddleware uses 'root' as the route when it's '/', which doesn't help us
    if len(route_pieces) == 1 and route_pieces[0] == 'root':
        route_pieces = []
    return {
        'name': p.name,
        'route': '/' + '/'.join(route_pieces),
        'timestamp': datetime.datetime.fromtimestamp(float(pieces[-2]), tz=timezone.utc),
        # The 'ms' suffix is hard coded in the default format string, it's always milliseconds
        'duration':  datetime.timedelta(milliseconds=int(pieces[-3].replace('ms', ''))),
        'svg_url': url_for('admin.profiling_viz_svg', name=p.name),
    }


def query_term_matches(term: str, profiling: Dict[str, Any]) -> bool:
    try:
        if term.startswith('<'):
            # Durations less than remainder of string
            max_dur = datetime.timedelta(milliseconds=int(term[1:]))
            return max_dur >= profiling['duration']
        elif term.startswith('>'):
            # Durations greater than remainder of string
            min_dur = datetime.timedelta(milliseconds=int(term[1:]))
            return min_dur <= profiling['duration']
        elif term.startswith('start:'):
            # Started on or after this date
            min_date = datetime.date(*map(int, term[6:].split('-')))
            return min_date <= profiling['timestamp'].date()
        elif term.startswith('end:'):
            # Started on or before this date
            max_date = datetime.date(*map(int, term[4:].split('-')))
            return max_date >= profiling['timestamp'].date()
        elif term.startswith('!'):
            # Match the route, inverted
            return term[1:] not in profiling.get('route', '')
        else:
            # Match the route
            return term in profiling.get('route', '')
    except:
        # Malformed search string
        return False


@admin.route("/admin/profiling_viz/<name>")
@adminrequired
def profiling_viz(name: str) -> Union[str, werkzeug.wrappers.Response]:
    prof_dir = _cfg('profile-dir')
    return (render_template("admin-profiling-viz.html",
                            profiling=parse_prof_filename(Path(prof_dir) / name))
            if prof_dir else redirect(url_for('admin.profiling', page=1)))


@admin.route("/admin/profiling_viz_svg/<name>")
@adminrequired
def profiling_viz_svg(name: str) -> Union[str, werkzeug.wrappers.Response]:
    prof_dir = _cfg('profile-dir')
    return (run(['flameprof', Path(prof_dir) / name], stdout=PIPE).stdout.decode('utf-8')
            if prof_dir else '')


@admin.route("/admin/users/<int:page>")
@adminrequired
def users(page: int) -> Union[str, werkzeug.wrappers.Response]:
    if page < 1:
        return redirect(url_for('admin.users', page=1, **request.args))
    show_non_public = (request.args.get('show_non_public', '').lower() in TRUE_STR)
    query = request.args.get('query', type=str)
    users = search_users(query.lower()) if query else User.query
    if not show_non_public:
        users = users.filter(User.public)
    users = users.order_by(desc(User.created))
    user_count = users.count()
    # We can limit here because SqlAlchemy executes queries lazily.
    users = users.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)

    total_pages = max(1, math.ceil(user_count / ITEMS_PER_PAGE))
    if page > total_pages:
        return redirect(url_for('admin.users', page=total_pages, **request.args))

    return render_template('admin-users.html',
                           users=users, page=page, total_pages=total_pages,
                           query=query, show_non_public=show_non_public)


@admin.route("/admin/blog")
@adminrequired
def blog() -> str:
    return render_template("admin-blog.html")


@admin.route("/admin/publishers/<int:page>")
@adminrequired
def publishers(page: int, error: str = None) -> Union[str, werkzeug.wrappers.Response]:
    if page < 1:
        return redirect(url_for('admin.publishers', page=1, **request.args))
    show_none_active = (request.args.get('show_none_active', '').lower() in TRUE_STR)
    query = request.args.get('query', type=str)
    publishers = search_publishers(query.lower()) if query else Publisher.query
    if not show_none_active:
        publishers = publishers.join(Publisher.games).filter(Game.active).distinct(Publisher.id)
    publishers = publishers.order_by(desc(Publisher.id))
    publisher_count = publishers.count()
    publishers = publishers.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)

    total_pages = max(1, math.ceil(publisher_count / ITEMS_PER_PAGE))
    if page > total_pages:
        return redirect(url_for('admin.publishers', page=total_pages, **request.args))

    return render_template('admin-publishers.html',
                           publishers=publishers, publisher_count=publisher_count, page=page,
                           total_pages=total_pages, query=query, show_none_active=show_none_active,
                           error=error)


@admin.route("/admin/games/<int:page>")
@adminrequired
def games(page: int, error: str = None) -> Union[str, werkzeug.wrappers.Response]:
    if page < 1:
        return redirect(url_for('admin.games', page=1, **request.args))
    show_inactive = (request.args.get('show_inactive', '').lower() in TRUE_STR)
    query = request.args.get('query', type=str)
    games = search_games(query.lower()) if query else Game.query
    if not show_inactive:
        games = games.filter(Game.active)
    games = games.order_by(desc(Game.id))
    game_count = games.count()
    games = games.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)

    total_pages = max(1, math.ceil(game_count / ITEMS_PER_PAGE))
    if page > total_pages:
        return redirect(url_for('admin.games', page=total_pages, **request.args))

    publishers = Publisher.query.order_by(desc(Publisher.id))

    return render_template('admin-games.html',
                           games=games, publishers=publishers, game_count=game_count,
                           page=page, total_pages=total_pages,
                           query=query, show_inactive=show_inactive,
                           error=error)


@admin.route("/admin/gameversions/<int:page>")
@adminrequired
def game_versions(page: int, error: str = None) -> Union[str, werkzeug.wrappers.Response]:
    if page < 1:
        return redirect(url_for('admin.game_versions', page=1, **request.args))
    show_inactive = (request.args.get('show_inactive', '').lower() in TRUE_STR)
    query = request.args.get('query', type=str)
    game_versions = search_game_versions(query.lower()) if query else GameVersion.query
    if not show_inactive:
        game_versions = game_versions.join(GameVersion.game).filter(Game.active)
    game_versions = game_versions.order_by(desc(GameVersion.id))
    game_version_count = game_versions.count()
    game_versions = game_versions.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)

    total_pages = max(1, math.ceil(game_version_count / ITEMS_PER_PAGE))
    if page > total_pages:
        return redirect(url_for('admin.game_versions', page=total_pages, **request.args))

    games = Game.query.order_by(desc(Game.id))

    return render_template('admin-game-versions.html',
                           game_versions=game_versions, games=games,
                           game_version_count=game_version_count,
                           page=page, total_pages=total_pages,
                           query=query, show_inactive=show_inactive,
                           error=error)


@admin.route("/admin/email", methods=['GET', 'POST'])
@adminrequired
def email() -> Union[str, werkzeug.wrappers.Response]:
    if request.method == 'GET':
        return render_template('admin-email.html')

    subject = request.form.get('subject')
    body = request.form.get('body')
    modders_only = request.form.get('modders-only') == 'on'
    if not subject or not body:
        abort(400)
    users = User.query
    if modders_only:
        users = db.query(User.email) \
            .filter(or_(User.username == current_user.username,
                        db.query(Mod.id).filter(Mod.user_id == User.id).exists()))
    send_bulk_email([u.email for u in users], subject, body)
    return redirect(url_for('admin.email'))


@admin.route("/admin/links")
@adminrequired
def links() -> str:
    return render_template('admin-links.html')


@admin.route("/admin/impersonate/<username>")
@adminrequired
def impersonate(username: str) -> werkzeug.wrappers.Response:
    user = User.query.filter(User.username == username).first()
    login_user(user)
    return redirect("/")


@admin.route("/publishers/create", methods=['POST'])
@adminrequired
@with_session
def create_publisher() -> werkzeug.wrappers.Response:
    name = request.form.get("pname")
    if not name:
        return publishers(1, 'Publisher name is required!')
    if any(Publisher.query.filter(Publisher.name == name)):
        return publishers(1, 'A publisher by that name already exists!')
    db.add(Publisher(name=name))
    db.commit()
    return redirect(url_for('admin.publishers', page=1, **request.args))


@admin.route("/games/create", methods=['POST'])
@adminrequired
@with_session
def create_game() -> werkzeug.wrappers.Response:
    name = request.form.get("gname")
    if not name:
        return games(1, 'Game name is required!')
    sname = request.form.get("sname")
    if not sname:
        return games(1, 'Short name is required!')
    pid = request.form.get("pname")
    if not pid:
        return games(1, 'Publisher is required!')
    if any(Game.query.filter(Game.name == name)):
        return games(1, 'A game by that name already exists!')
    db.add(Game(name=name, publisher_id=pid, short=sname, active=True))
    db.commit()
    return redirect(url_for('admin.games', page=1, **request.args))


@admin.route("/versions/create", methods=['POST'])
@adminrequired
@with_session
def create_version() -> werkzeug.wrappers.Response:
    friendly = request.form.get("friendly_version")
    if not friendly:
        return game_versions(1, 'Version name is required!')
    gid = request.form.get("ganame")
    if not gid:
        return game_versions(1, 'Game is required!')
    if any(GameVersion.query.filter(
            GameVersion.game_id == gid,
            GameVersion.friendly_version == friendly)):
        return game_versions(1, 'A version by that name already exists for that game!')
    db.add(GameVersion(friendly_version=friendly, game_id=gid))
    db.commit()
    return redirect(url_for('admin.game_versions', page=1, **request.args))


@admin.route("/admin/manual-confirmation/<int:user_id>")
@adminrequired
@with_session
def manual_confirm(user_id: int) -> werkzeug.wrappers.Response:
    user = User.query.get(user_id)
    if not user:
        abort(404)
    user.confirmation = None
    return redirect(url_for('profile.view_profile', username=user.username))


@admin.route("/admin/grant-admin/<int:user_id>", methods=['POST'])
@adminrequired
@with_session
def grant_admin(user_id: int) -> werkzeug.wrappers.Response:
    user = User.query.get(user_id)
    if not user:
        abort(404)
    user.admin = True
    return redirect(url_for('profile.view_profile', username=user.username))


def search_users(query: str) -> Query:
    return User.query.filter(
        func.lower(User.username).contains(query) |
        func.lower(User.email).contains(query) |
        func.lower(User.description).contains(query) |
        func.lower(User.forumUsername).contains(query) |
        func.lower(User.ircNick).contains(query) |
        func.lower(User.redditUsername).contains(query) |
        func.lower(User.twitterUsername).contains(query)
    )


def search_publishers(query: str) -> Query:
    return Publisher.query.filter(
        func.lower(Publisher.name).contains(query) |
        func.lower(Publisher.short_description).contains(query) |
        func.lower(Publisher.description).contains(query) |
        func.lower(Publisher.link).contains(query)
    )


def search_games(query: str) -> Query:
    return Game.query.join(Game.publisher).filter(
        func.lower(Game.name).contains(query) |
        func.lower(Game.altname).contains(query) |
        func.lower(Game.short).contains(query) |
        func.lower(Game.short_description).contains(query) |
        func.lower(Game.description).contains(query) |
        func.lower(Game.link).contains(query) |
        func.lower(Publisher.name).contains(query) |
        (search_publishers(query).filter(Publisher.id == Game.publisher_id).count() > 0)
    )


def search_game_versions(query: str) -> Query:
    return GameVersion.query.filter(
        func.lower(GameVersion.friendly_version).contains(query) |
        (search_games(query).filter(Game.id == GameVersion.game_id).count() > 0)
    )
