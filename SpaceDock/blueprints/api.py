"""
SpaceDock API v2
New route structure with game_id prefix for all resource routes.
"""
import math
import json
import os
import time
import re
import zipfile
from datetime import datetime
from functools import wraps
from shutil import rmtree
from typing import Dict, Any, Callable, Optional, Tuple, Iterable, List, Union

from flask import Blueprint, url_for, current_app, request, abort
from flask_login import login_user, current_user, logout_user
from sqlalchemy import desc, asc
from sqlalchemy.orm import Query
from werkzeug.utils import secure_filename

from .accounts import check_password_criteria
from ..notification import send_add_notifications, send_change_notifications
from ..common import json_output, paginate_query, with_session, get_paginated_mods, json_response, \
    check_mod_editable, check_pack_editable, set_game_info, TRUE_STR, get_page, render_markdown
from ..config import _cfg, _cfgi
from ..database import db
from ..email import send_update_notification, send_grant_notice, send_password_changed
from ..objects import GameVersion, Game, Publisher, Mod, Featured, User, ModVersion, SharedAuthor, \
    ModList, EnabledNotification
from ..search import search_mods, search_users, typeahead_mods, get_mod_score
from ..thumbnail import thumb_path_from_background_path
from ..antivirus import file_contains_malware, quarantine_malware, punish_malware
from ..purge import purge_download

api = Blueprint('api', __name__)

default_description = """This is your mod listing! You can edit it as much as you like before you make it public.

To edit **this** text, you can click on the "**Edit this Mod**" button up there.

By the way, you have a lot of flexibility here. You can embed YouTube videos or screenshots. Be creative.

You can check out the SpaceDock [markdown documentation](/markdown) for tips.

Thanks for hosting your mod on SpaceDock!"""

SOURCE_USER_REPO_PATTERN = re.compile(
    r'^https://github.com/(?P<user>[^/]+)/(?P<repo>[^/]+)/?')


# =============================================================================
# Helper functions
# =============================================================================

def user_info(user: User) -> Dict[str, Any]:
    return {
        "username": user.username,
        "description": user.description,
        "forumUsername": user.forumUsername,
        "ircNick": user.ircNick,
        "twitterUsername": user.twitterUsername,
        "redditUsername": user.redditUsername
    }


def mod_info(mod: Mod) -> Dict[str, Any]:
    return {
        "name": mod.name,
        "id": mod.id,
        "game": mod.game.name,
        "game_id": mod.game_id,
        "short_description": mod.short_description,
        "downloads": mod.download_count,
        "followers": mod.follower_count,
        "author": mod.user.username,
        "shared_authors": list(),
        "background": mod.background_url(_cfg('protocol'), _cfg('cdn-domain')),
        "bg_offset_y": mod.bgOffsetY,
        "license": mod.license,
        "website": mod.external_link,
        "donations": mod.donation_link,
        "source_code": mod.source_link,
        "url": url_for("mods.mod", gameshort=mod.game.short, modcategory=mod.category.stub if mod.category else "general", mod_id=mod.id, mod_name=mod.name)
    }


def version_info(mod: Mod, version: ModVersion) -> Dict[str, Any]:
    return {
        "friendly_version": version.friendly_version,
        "game_version": version.gameversion.friendly_version,
        "id": version.id,
        "created": version.created,
        "download_path": url_for('mods.download', gameshort=mod.game.short,
                                 modcategory=mod.category.stub,
                                 mod_id=mod.id, mod_name=mod.name,
                                 version=version.friendly_version),
        "changelog": version.changelog,
        "downloads": version.download_count,
    }


def game_version_info(version: ModVersion) -> Dict[str, str]:
    return {
        "id": version.id,
        "friendly_version": version.friendly_version
    }


def game_info(game: Game) -> Dict[str, str]:
    return {
        "id": game.id,
        "name": game.name,
        "short": game.short,
        "active": game.active
    }


def publisher_info(publisher: Publisher) -> Dict[str, str]:
    return {
        "id": publisher.id,
        "name": publisher.name,
        "type": publisher.type,
        "avatar": publisher.avatar_url(),
        "bio": publisher.bio,
    }


def pack_info(pack: ModList) -> Dict[str, Any]:
    return {
        "id": pack.id,
        "name": pack.name,
        "description": pack.short_description,
        "game": pack.game.name if pack.game else None,
        "game_id": pack.game_id,
        "author": pack.user.username if pack.user else None,
        "created": pack.created.isoformat() if pack.created else None,
    }


def user_required(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user or not current_user.is_authenticated:
            abort(json_response({'error': True, 'reason': 'Not authenticated.'}, 403))
        return func(*args, **kwargs)
    return wrapper


def _get_mod(mod_id: int) -> Mod:
    mod = Mod.query.get(mod_id)
    if not mod:
        abort(json_response({'error': True, 'reason': 'Mod does not exist.'}, 404))
    return mod

def _get_category_mod(category_stub: str, mod_id: int) -> Mod:
    """Get mod by ID and validate it belongs to the specified category."""
    mod = _get_mod(mod_id)
    if not mod.category or mod.category.stub != category_stub:
        abort(json_response({'error': True, 'reason': 'Mod not in category.'}, 404))
    return mod


def _check_mod_published(mod: Mod) -> None:
    if not mod.published:
        abort(json_response({'error': True, 'reason': 'Mod not published.'}, 403))


def _check_mod_editable(mod: Mod) -> None:
    check_mod_editable(mod, json_response({'error': True, 'reason': 'Not enough rights.'}, 403))


def _get_mod_pending_author(mod: Mod) -> User:
    author = next((a for a in mod.shared_authors if a.user == current_user), None)
    if not author:
        abort(json_response({'error': True, 'reason': 'Not invited.'}, 403))
    return author


def _update_image(old_path: str, base_name: str, base_path: str) -> Optional[str]:
    f = request.files.get('image')
    if f is None:
        return None
    if not f.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        abort(json_response({'error': True,
                              'reason': 'Unacceptable file extension: {}'.format(f.filename)}, 400))
    try:
        filename = secure_filename(f"{base_name}-{int(time.time())}-{f.filename}")
    except ValueError:
        abort(json_response({'error': True, 'reason': 'Invalid filename.'}, 400))
    fpath = os.path.join(base_path, filename)
    try:
        f.save(fpath)
    except Exception:
        abort(json_response({'error': True,
                              'reason': 'Failed to upload file.'}, 500))
    if fpath and file_contains_malware(fpath):
        quarantine_malware(fpath)
        punish_malware(base_name)
        return None
    if old_path and old_path != fpath:
        try_remove_file_and_folder(old_path)
    return os.path.join(base_path, filename)


def try_remove_file_and_folder(path: str) -> None:
    """Tries to remove a file and the containing folder if empty
    """
    try:
        os.unlink(path)
    except OSError:
        pass
    except PermissionError:
        pass
    try:
        rmtree(path)
    except OSError:
        pass


def _get_modversion_paths(mod_name: str, friendly_version: str) -> Tuple[str, str]:
    mod_name_sec = secure_filename(mod_name)
    base_path = os.path.join(_cfg('storage'), mod_name_sec)
    if not os.path.isdir(base_path):
        os.makedirs(base_path)
    full_path = os.path.join(base_path, friendly_version)
    if not os.path.isdir(full_path):
        os.makedirs(full_path)
    return full_path, os.path.join(base_path, filename)


def serialize_mod_list(mods: Iterable[Mod]) -> Iterable[Dict[str, Any]]:
    results = list()
    for mod in mods:
        info = mod_info(mod)
        info['versions'] = list()
        results.append(info)
    return results


# =============================================================================
# Game Routes
# =============================================================================

@api.route("/api/game/all")
@json_output
def games_list() -> List[Dict[str, Any]]:
    results = list()
    for game in Game.query:
        results.append(game_info(game))
    return results


@api.route("/api/game/<game_id>")
@json_output
def game_info_api(game_id: int) -> Dict[str, Any]:
    game = Game.query.get(game_id)
    if not game:
        abort(json_response({'error': True, 'reason': 'Game not found.'}, 404))
    return game_info(game)


@api.route("/api/game/<game_id>/version/all")
@json_output
def gameversions_list(game_id: int) -> List[Dict[str, Any]]:
    versions = GameVersion.query.filter_by(game_id=game_id).order_by(desc(GameVersion.id))
    results = list()
    for version in versions:
        results.append(game_version_info(version))
    return results


@api.route("/api/game/<game_id>/category/all")
@json_output
def gamecategories_list(game_id: int) -> List[Dict[str, Any]]:
    game = Game.query.get(game_id)
    if not game:
        abort(json_response({'error': True, 'reason': 'Game not found.'}, 404))
    results = list()
    for setting in game.mod_category_settings:
        if setting.category and setting.enabled:
            results.append({
                "id": setting.category.id,
                "name": setting.category.name,
                "stub": setting.category.stub
            })
    return results
@api.route("/api/game/<game_id>/category", methods=['POST'])
@user_required
@json_output
def create_category(game_id: int) -> Dict[str, Any]:
    if not current_user.admin:
        abort(json_response({'error': True, 'reason': 'Admin required.'}, 403))
    name = request.form.get('name')
    slug = request.form.get('slug')
    description = request.form.get('description', '')
    if not name or not slug:
        abort(json_response({'error': True, 'reason': 'Missing name or slug.'}, 400))
    cat = ModCategory(name=name, stub=slug)
    db.session.add(cat)
    db.session.commit()
    return {"id": cat.id, "name": cat.name, "slug": cat.stub, "sort_order": cat.id}


@api.route("/api/game/<game_id>/category/<category_id>", methods=['PUT'])
@user_required
@json_output
def update_category(game_id: int, category_id: int) -> Dict[str, Any]:
    if not current_user.admin:
        abort(json_response({'error': True, 'reason': 'Admin required.'}, 403))
    cat = db.session.get(ModCategory, category_id)
    if not cat:
        abort(json_response({'error': True, 'reason': 'Category not found.'}, 404))
    name = request.form.get('name', cat.name)
    slug = request.form.get('slug', cat.stub)
    description = request.form.get('description', '')
    cat.name = name
    cat.stub = slug
    db.session.commit()
    return {"id": cat.id, "name": cat.name, "slug": cat.stub, "sort_order": cat.id}


@api.route("/api/game/<game_id>/category/<category_id>", methods=['DELETE'])
@user_required
@json_output
def delete_category(game_id: int, category_id: int) -> Dict[str, Any]:
    if not current_user.admin:
        abort(json_response({'error': True, 'reason': 'Admin required.'}, 403))
    cat = db.session.get(ModCategory, category_id)
    if not cat:
        abort(json_response({'error': True, 'reason': 'Category not found.'}, 404))
    db.session.delete(cat)
    db.session.commit()
    return {"error": False}



@api.route("/api/game/<game_id>/notification/all")
@json_output
def game_notifications_list(game_id: int) -> List[Dict[str, Any]]:
    game = Game.query.get(game_id)
    if not game:
        abort(json_response({'error': True, 'reason': 'Game not found.'}, 404))
    return [
        {'id': n.id, 'name': n.name,
         'add_url': n.add_url, 'change_url': n.change_url}
        for n in game.notifications
    ]


@api.route("/api/game/<game_id>/background", methods=['POST'])
@with_session
@json_output
@user_required
def update_game_background(game_id: int) -> Dict[str, Any]:
    game = Game.query.get(game_id)
    if not game:
        abort(json_response({'error': True, 'reason': 'Game not found.'}, 404))
    if not current_user.admin:
        abort(json_response({'error': True, 'reason': 'Not admin.'}, 403))
    old_bg = game.background
    path = _update_image(old_bg, game.short, _cfg('storage'))
    if path:
        game.background = path
        db.commit()
    return {'path': None}


# =============================================================================
# Publisher Routes
# =============================================================================

@api.route("/api/publisher/all")
@json_output
def publishers_list() -> List[Dict[str, Any]]:
    results = list()
    for publisher in Publisher.query:
        results.append(publisher_info(publisher))
    return results


@api.route("/api/publisher/<publisher_id>")
@json_output
def publisher_info_api(publisher_id: int) -> Dict[str, Any]:
    publisher = Publisher.query.get(publisher_id)
    if not publisher:
        abort(json_response({'error': True, 'reason': 'Publisher not found.'}, 404))
    return publisher_info(publisher)


# =============================================================================
# Browse & Search Routes
# =============================================================================

def game_filters(query: Query, game_id: Optional[int], game_version_id: Optional[int],
                 game_version: Optional[str]) -> Query:
    if game_version_id:
        query = query.filter(ModVersion.id == game_version_id)
    elif game_version:
        query = query.join(ModVersion) \
            .filter(ModVersion.gameversion_id == game_version)
    if game_id:
        query = query.filter(Mod.game_id == game_id)
    return query


@api.route("/api/game/<game_id>/<category_stub>/browse/all")
@json_output
def browse(game_id: int, category_stub: str) -> Dict[str, Any]:
    per_page = request.args.get('count', 30)
    sort = request.args.get('sort')
    sort_order = request.args.get('order')

    query = Mod.query
    query = game_filters(query, game_id, None, None)

    if sort == 'downloads':
        query = query.order_by(desc(Mod.download_count))
    elif sort == 'name':
        query = query.order_by(Mod.name)
    else:
        query = query.order_by(desc(Mod.id))

    if sort_order == 'asc':
        query = query.order_by(asc(Mod.id))

    count = query.count()
    total_pages = max(math.ceil(count / per_page), 1)
    mods, page, _ = paginate_query(query)
    return {
        "total": count,
        "count": per_page,
        "pages": total_pages,
        "page": page,
        "result": serialize_mod_list(mods)
    }


@api.route("/api/game/<game_id>/<category_stub>/browse/new")
@json_output
def browse_new(game_id: int, category_stub: str) -> Iterable[Dict[str, Any]]:
    query = Mod.query.filter(Mod.published == True)
    query = game_filters(query, game_id, None, None)
    query = query.order_by(desc(Mod.id))
    mods, page, total_pages = paginate_query(query)
    return serialize_mod_list(mods)


@api.route("/api/game/<game_id>/<category_stub>/browse/top")
@json_output
def browse_top(game_id: int, category_stub: str) -> Iterable[Dict[str, Any]]:
    game = Game.query.get(game_id)
    mods, *_ = get_paginated_mods(ga=game)
    return serialize_mod_list(mods)


@api.route("/api/game/<game_id>/<category_stub>/browse/featured")
@json_output
def browse_featured(game_id: int, category_stub: str) -> Iterable[Dict[str, Any]]:
    mods = Featured.query.join(Mod).filter(Mod.game_id == game_id) \
        .order_by(Featured.priority.desc())
    featured_mods = [f.mod for f in mods]
    return serialize_mod_list(featured_mods)


@api.route("/api/game/<game_id>/<category_stub>/search/suggest")
@json_output
def typeahead_mod(game_id: int, category_stub: str) -> Iterable[Dict[str, Any]]:
    query = request.args.get('query', '')
    results = typeahead_mods(game_id, query)
    return serialize_mod_list(results)


@api.route("/api/game/<game_id>/<category_stub>/search")
@json_output
def search_mod(game_id: int, category_stub: str) -> Iterable[Dict[str, Any]]:
    query = request.args.get('query')
    page = get_page()
    mods, page, total_pages = search_mods(game_id, query, page, 30)
    return serialize_mod_list(mods)


@api.route("/api/game/<game_id>/<category_stub>/browse/extended")
@json_output
def browse_extended(game_id: int, category_stub: str) -> Dict[str, Any]:
    """Browse mods with extended filters: published status, tags, downloads, date."""
    published = request.args.get('published')
    min_downloads = request.args.get('min_downloads')
    created_after = request.args.get('created_after')

    query = Mod.query
    query = game_filters(query, game_id, None, None)

    if published == 'true' or published == '1':
        query = query.filter(Mod.published == True)
    elif published == 'false' or published == '0':
        query = query.filter(Mod.published == False)

    if min_downloads:
        try:
            min_dl = int(min_downloads)
            query = query.filter(Mod.download_count >= min_dl)
        except ValueError:
            pass

    if created_after:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(created_after)
            query = query.filter(Mod.created >= dt)
        except ValueError:
            pass

    query = query.order_by(desc(Mod.id))
    mods, page, total_pages = paginate_query(query)
    return {
        'page': page,
        'pages': total_pages,
        'mods': serialize_mod_list(mods)
    }


@api.route("/api/game/<game_id>/<category_stub>/search/extended")
@json_output
def search_extended(game_id: int, category_stub: str) -> Dict[str, Any]:
    """Search mods with extended filters and sorting."""
    query_str = request.args.get('query')
    sort = request.args.get('sort')
    sort_order = request.args.get('order')
    published = request.args.get('published')

    page = get_page()
    mods, total = search_mods(game_id, query_str, page, 30)
    total_pages = max(1, -(-total // 30))

    if sort == 'downloads':
        mods.sort(key=lambda m: m.download_count, reverse=True)
    elif sort == 'name':
        mods.sort(key=lambda m: m.name)
    elif sort_order == 'asc':
        mods = list(reversed(mods))

    if published == 'true' or published == '1':
        mods = [m for m in mods if m.published]
    elif published == 'false' or published == '0':
        mods = [m for m in mods if not m.published]


    return {
        'page': page,
        'pages': total_pages,
        'mods': serialize_mod_list(mods)
    }

@api.route("/api/user/search")
@json_output
def search_user() -> Iterable[Dict[str, Any]]:
    query = request.args.get('query')
    page = get_page() - 1  # Convert 1-indexed to 0-indexed
    users = list(search_users(query, page))
    results = list()
    for user in users:
        info = user_info(user)
        info['id'] = user.id
        results.append(info)
    return results


# =============================================================================
# Authentication Routes
# =============================================================================

@api.route("/api/user/login", methods=['POST'])
@json_output
def login() -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return {'error': True, 'reason': 'Missing credentials.'}, 400
    user = User.query.filter(User.username == username).first()
    if user and user.check_password(password):
        login_user(user)
        return {'error': False}
    return {'error': True, 'reason': 'Invalid credentials.'}, 401


# =============================================================================
# User Routes
# =============================================================================

@api.route("/api/user/<username>")
@json_output
def user_info_api(username: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    user = User.query.filter(User.username == username).first()
    if not user:
        abort(json_response({'error': True, 'reason': 'User not found.'}, 404))
    info = user_info(user)
    info['id'] = user.id
    return info


@api.route('/api/user/<username>/password', methods=['POST'])
@with_session
@user_required
@json_output
def change_password(username: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    if current_user.username != username:
        return {'error': True, 'reason': 'Wrong user.'}, 403
    old_pw = request.form.get('password')
    new_pw = request.form.get('confirm_password')
    if not current_user.check_password(old_pw):
        return {'error': True, 'reason': 'Incorrect password.'}
    pw_message = check_password_criteria(new_pw)
    if pw_message is not None:
        return {'error': True, 'reason': pw_message}
    current_user.password = new_pw
    db.commit()
    send_password_changed(current_user)
    return {'error': False}


@api.route("/api/user/<username>", methods=['DELETE'])
@with_session
@user_required
@json_output
def delete_user(username: str) -> Tuple[Dict[str, Any], int]:
    if current_user.username != username:
        return {'error': True, 'reason': 'Wrong user.'}, 403
    user = User.query.filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
    return {"error": False}, 200


@api.route("/api/user/<username>/creation/all")
@json_output
def user_creations(username: str) -> Dict[str, Any]:
    """List all mods created by a user."""
    published = request.args.get('published')
    user = User.query.filter(User.username == username).first()
    if not user:
        abort(json_response({'error': True, 'reason': 'User not found.'}, 404))
    query = Mod.query.filter(Mod.user_id == user.id)
    if published == 'true' or published == '1':
        query = query.filter(Mod.published == True)
    elif published == 'false' or published == '0':
        query = query.filter(Mod.published == False)
    mods, page, total_pages = paginate_query(query.order_by(desc(Mod.id)))
    return {
        'page': page,
        'pages': total_pages,
        'mods': serialize_mod_list(mods)
    }


@api.route("/api/user/<username>/pack/all")
@json_output
def user_packs(username: str) -> Dict[str, Any]:
    """List all packs created by a user."""
    user = User.query.filter(User.username == username).first()
    if not user:
        abort(json_response({'error': True, 'reason': 'User not found.'}, 404))
    query = ModList.query.filter(ModList.user_id == user.id)
    packs, page, total_pages = paginate_query(query.order_by(desc(ModList.id)))
    return {
        'page': page,
        'pages': total_pages,
        'packs': [pack_info(p) for p in packs]
    }


@api.route('/api/user/<username>/background', methods=['POST'])
@with_session
@json_output
@user_required
def update_user_background(username: str) -> Dict[str, Any]:
    user = User.query.filter(User.username == username).first()
    if not user:
        abort(json_response({'error': True, 'reason': 'User not found.'}, 404))
    if not current_user.admin and current_user.username != username:
        abort(json_response({'error': True, 'reason': 'Not your profile.'}, 403))
    old_bg = user.background
    path = _update_image(old_bg, username, _cfg('storage'))
    if path:
        user.background = path
        db.commit()
    return {'path': None}


# =============================================================================
# Legacy Redirect Routes (game_id derived from mod_id)
# =============================================================================

@api.route("/api/mod/<int:mod_id>")
@json_output
def legacy_mod_info_redirect(mod_id: int) -> Dict[str, Any]:
    mod = _get_mod(mod_id)
    _check_mod_published(mod)
    return mod_info(mod)


@api.route("/api/mod/<int:mod_id>/<version>")
@json_output
def legacy_mod_version_redirect(mod_id: int, version: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    mod = _get_mod(mod_id)
    _check_mod_published(mod)
    if version == "latest" or version == "latest_version":
        ver = mod.default_version
    elif version.isdigit():
        ver = ModVersion.query.filter_by(mod_id=mod_id, id=int(version)).first()
    else:
        ver = ModVersion.query.filter_by(mod_id=mod_id, friendly_version=version).first()
    if not ver:
        abort(json_response({'error': True, 'reason': 'Version not found.'}, 404))
    return version_info(mod, ver)


@api.route("/api/ksp-avc/<int:mod_id>")
@json_output
def legacy_remote_version_file_redirect(mod_id: int) -> Dict[str, Any]:
    mod = _get_mod(mod_id)
    _check_mod_published(mod)
    return {
        "name": mod.name,
        "version": mod.default_version.friendly_version,
        "website": mod.external_link,
        "download": url_for('mods.download', mod_id=mod.id,
                            mod_name=mod.name,
                            version=mod.default_version.friendly_version),
    }


# =============================================================================
# New API Mod Info Routes
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>")
@json_output
def mod_info_by_id(game_id: int, category_stub: str, mod_id: int) -> Dict[str, Any]:
    """Get mod info by game_id and mod_id (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_published(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    return {
        "id": mod.id,
        "name": mod.name,
        "description": mod.short_description,
        "game": {"id": mod.game_id, "name": mod.game.name},
        "publisher": mod.user.username,
        "downloads": mod.download_count,
        "likes": mod.follower_count,
        "published_at": mod.created.isoformat() if mod.created else None,
        "updated_at": mod.updated.isoformat() if mod.updated else None,
        "default_version": mod.default_version.friendly_version if mod.default_version else None,
        # Legacy-compatible fields
        "author": mod.user.username,
        "game_id": mod.game_id,
        "short_description": mod.short_description,
        "followers": mod.follower_count,
        "default_version_id": mod.default_version.id if mod.default_version else None,
        "shared_authors": list(),
        "background": mod.background_url(_cfg('protocol'), _cfg('cdn-domain')),
        "bg_offset_y": mod.bgOffsetY,
        "license": mod.license,
        "website": mod.external_link,
        "donations": mod.donation_link,
        "source_code": mod.source_link,
        "url": url_for("mods.mod", gameshort=mod.game.short,
                        modcategory=mod.category.stub if mod.category else "general",
                        mod_id=mod.id, mod_name=mod.name)
    }


# Legacy redirect: /api/games -> /api/game/all
@api.route("/api/games")
@json_output
def legacy_games_list() -> List[Dict[str, Any]]:
    """Legacy route: redirect to new games list."""
    return games_list()


# =============================================================================
# Mod Management Routes (legacy redirects)
# =============================================================================

@api.route('/api/mod/<int:mod_id>/update-bg', methods=['POST'])
@with_session
@json_output
@user_required
def legacy_update_mod_bg_redirect(mod_id: int) -> Dict[str, Any]:
    mod = _get_mod(mod_id)
    _check_mod_editable(mod)
    old_bg = mod.background
    path = _update_image(old_bg, mod.name, _cfg('storage'))
    if path:
        mod.background = path
        db.commit()
    return {'path': None}


@api.route('/api/mod/<int:mod_id>/grant', methods=['POST'])
@with_session
@json_output
def legacy_grant_redirect(mod_id: int) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    mod = _get_mod(mod_id)
    _check_mod_editable(mod)
    username = request.form.get('username')
    if not username:
        return {'error': True, 'reason': 'Missing username.'}
    user = User.query.filter(User.username == username).first()
    if not user:
        return {'error': True, 'reason': 'User does not exist.'}
    shared_author = SharedAuthor(user=user, mod=mod)
    db.add(shared_author)
    db.commit()
    send_grant_notice(mod, user)
    return {'error': False}


@api.route('/api/mod/<mod_id>/accept_grant', methods=['POST'])
@with_session
@json_output
@user_required
def legacy_accept_grant_redirect(mod_id: int) -> Tuple[Dict[str, Any], int]:
    mod = _get_mod(mod_id)
    _get_mod_pending_author(mod)
    return {'error': False}, 200


@api.route('/api/mod/<mod_id>/reject_grant', methods=['POST'])
@with_session
@json_output
@user_required
def legacy_reject_grant_redirect(mod_id: int) -> Tuple[Dict[str, Any], int]:
    mod = _get_mod(mod_id)
    _get_mod_pending_author(mod)
    return {'error': False}, 200


@api.route('/api/mod/<mod_id>/revoke', methods=['POST'])
@with_session
@json_output
@user_required
def legacy_revoke_redirect(mod_id: int) -> Tuple[Dict[str, Any], int]:
    mod = _get_mod(mod_id)
    _check_mod_editable(mod)
    username = request.form.get('username')
    author = next((a for a in mod.shared_authors if a.user.username == username), None)
    if author:
        db.delete(author)
        db.commit()
    return {'error': False}, 200


@api.route('/api/mod/<int:mod_id>/set-default/<int:vid>', methods=['POST'])
@with_session
@json_output
def legacy_set_default_redirect(mod_id: int, vid: int) -> Tuple[Dict[str, Any], int]:
    mod = _get_mod(mod_id)
    _check_mod_editable(mod)
    ver = ModVersion.query.filter_by(id=vid).first()
    if ver and ver.mod_id == mod_id:
        mod.default_version = ver
        db.commit()
    return {'error': False}, 200


@api.route('/api/pack/create', methods=['POST'])
@json_output
@with_session
@user_required
def create_list() -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    if not current_user.public:
        return {'error': True, 'reason': 'Profile not public.'}, 403
    name = request.form.get('name')
    description = request.form.get('description')
    game_id = request.form.get('game_id')
    mod_list = ModList(name=name, description=description, game_id=game_id)
    mod_list.user = current_user
    db.add(mod_list)
    db.commit()
    return {'url': '/lists/' + str(mod_list.id)}


@api.route('/api/mod/create', methods=['POST'])
@json_output
@user_required
def legacy_mod_create_redirect() -> Tuple[Dict[str, Any], int]:
    if not current_user.public:
        return {'error': True, 'reason': 'Profile not public.'}, 403
    game_id = request.form.get('game_id')
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description') or default_description

    if not name or not game_id or not category:
        return {'error': True, 'reason': 'Missing required fields.'}, 400

    mod = Mod(name=name, game_id=game_id, category_id=category)
    mod.user = current_user
    mod.short_description = description[:250]
    mod.description = description
    db.add(mod)
    db.commit()

    send_add_notifications(mod)

    return {'url': url_for("mods.mod", mod_id=mod.id, mod_name=mod.name)}, 201


@api.route('/api/mod/<int:mod_id>/update', methods=['POST'])
@with_session
@json_output
@user_required
def legacy_mod_update_redirect(mod_id: int) -> Tuple[Dict[str, Any], int]:
    mod = _get_mod(mod_id)
    _check_mod_editable(mod)

    name = request.form.get('name')
    if name:
        mod.name = name

    description = request.form.get('description')
    if description:
        mod.description = description
        mod.short_description = description[:250]

    category = request.form.get('category')
    if category:
        mod.category_id = category

    license = request.form.get('license')
    if license:
        mod.license = license

    external_link = request.form.get('external_link')
    if external_link:
        mod.external_link = external_link

    donation_link = request.form.get('donation_link')
    if donation_link:
        mod.donation_link = donation_link

    source_link = request.form.get('source_link')
    if source_link:
        mod.source_link = source_link

    published = request.form.get('published', '') in TRUE_STR
    mod.published = published

    db.commit()

    if published:
        send_change_notifications(mod)

    return {}, 200


@api.route('/api/mod/<int:mod_id>/edit_version', methods=['POST'])
@with_session
@json_output
@user_required
def legacy_edit_version_redirect(mod_id: int) -> Tuple[Dict[str, Any], int]:
    mod = _get_mod(mod_id)
    _check_mod_editable(mod)

    friendly_version = request.form.get('friendly_version')
    gameversion_id = request.form.get('gameversion_id')
    if not friendly_version or not gameversion_id:
        return {'error': True, 'reason': 'Missing version info.'}, 400

    ver = ModVersion(mod=mod, friendly_version=friendly_version,
                     gameversion_id=gameversion_id)
    db.add(ver)
    db.commit()

    return {'url': url_for('mods.mod_version', mod_id=mod.id, mod_name=mod.name,
                           version=friendly_version)}, 201


# =============================================================================
# Download Stats
# =============================================================================

@api.route("/api/download_counts", methods=['POST'])
@json_output
def download_counts() -> Tuple[Dict[str, Any], int]:
    return {
        "error": True,
        "reason": "This API endpoint is no longer supported."
    }, 501
# =============================================================================
# New API: Version Routes
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/version/all")
@json_output
def versions_list(game_id: int, category_stub: str, mod_id: int) -> List[Dict[str, Any]]:
    """List all versions for a mod (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_published(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    return [version_info(mod, v) for v in mod.versions]

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/version/<int:vid>")
@json_output
def version_info_api(game_id: int, category_stub: str, mod_id: int, vid: int) -> Dict[str, Any]:
    """Get specific version info (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_published(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    ver = ModVersion.query.filter_by(id=vid, mod_id=mod_id).first()
    if not ver:
        abort(json_response({'error': True, 'reason': 'Version not found.'}, 404))
    return version_info(mod, ver)

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/version/<int:vid>")
@with_session
@json_output
@user_required
def edit_version_new(game_id: int, category_stub: str, mod_id: int, vid: int) -> Tuple[Dict[str, Any], int]:
    """Edit version (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))

    friendly_version = request.form.get('friendly_version')
    gameversion_id = request.form.get('gameversion_id')
    if not friendly_version or not gameversion_id:
        return {'error': True, 'reason': 'Missing version info.'}, 400

    ver = ModVersion(mod=mod, friendly_version=friendly_version,
                     gameversion_id=gameversion_id)
    db.add(ver)
    db.commit()

    return {'version': ver.friendly_version}, 201

# =============================================================================
# New API: AVC Version File
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/avc")
@json_output
def avc_version_file(game_id: int, category_stub: str, mod_id: int) -> Dict[str, Any]:
    """Remote version file in AVC format (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_published(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    return {
        "name": mod.name,
        "version": mod.default_version.friendly_version if mod.default_version else "0.0.0",
        "website": mod.external_link,
        "download": url_for('mods.download', gameshort=mod.game.short,
                            modcategory=mod.category.stub,
                            mod_id=mod.id, mod_name=mod.name,
                            version=mod.default_version.friendly_version if mod.default_version else "0.0.0"),
    }

# =============================================================================
# New API: Download Stats
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>/download/stat", methods=['POST'])
@json_output
def download_stats(game_id: int, category_stub: str) -> Tuple[Dict[str, Any], int]:
    """Download statistics (new API structure)."""
    mod_ids = json.loads(request.form.get('mod_ids', '[]'))
    results = {}
    for mid in mod_ids:
        mod = _get_mod(mid)
        results[mid] = mod.download_count
    return results, 200

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/download/stat")
@json_output
def single_mod_download_stats(game_id: int, category_stub: str, mod_id: int) -> Dict[str, Any]:
    """Download stats for single mod (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    return {"mod_id": mod.id, "count": mod.download_count}

# =============================================================================
# New API: Mod Management
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>", methods=['POST'])
@with_session
@json_output
@user_required
def create_mod_new(game_id: int, category_stub: str) -> Tuple[Dict[str, Any], int]:
    """Create new mod (new API structure)."""
    if not current_user.public:
        return {'error': True, 'reason': 'Profile not public.'}, 403

    name = request.form.get('name')
    description = request.form.get('description') or default_description

    if not name:
        return {'error': True, 'reason': 'Missing name.'}, 400

    category = None
    for setting in Game.query.get(game_id).mod_category_settings:
        if setting.category and setting.category.stub == category_stub:
            category = setting.category
            break
    if not category:
        abort(json_response({'error': True, 'reason': 'Category not found for game.'}, 404))

    mod = Mod(name=name, game_id=game_id, category_id=category.id)
    mod.user = current_user
    mod.short_description = description[:250]
    mod.description = description
    db.add(mod)
    db.commit()

    send_add_notifications(mod)

    return {'id': mod.id, 'name': mod.name, 'game': {'id': mod.game_id, 'name': mod.game.name}}, 201

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>", methods=['PUT'])
@with_session
@json_output
@user_required
def update_mod_new(game_id: int, category_stub: str, mod_id: int) -> Tuple[Dict[str, Any], int]:
    """Update mod (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))

    name = request.form.get('name')
    if name:
        mod.name = name

    description = request.form.get('description')
    if description:
        mod.description = description
        mod.short_description = description[:250]

    license = request.form.get('license')
    if license:
        mod.license = license

    external_link = request.form.get('external_link')
    if external_link:
        mod.external_link = external_link

    donation_link = request.form.get('donation_link')
    if donation_link:
        mod.donation_link = donation_link

    source_link = request.form.get('source_link')
    if source_link:
        mod.source_link = source_link

    published = request.form.get('published', '') in TRUE_STR
    mod.published = published

    db.commit()

    if published:
        send_change_notifications(mod)

    return {'id': mod.id, 'name': mod.name, 'game': {'id': mod.game_id, 'name': mod.game.name}}, 200

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>", methods=['DELETE'])
@with_session
@json_output
@user_required
def delete_mod_new(game_id: int, category_stub: str, mod_id: int) -> Tuple[Dict[str, Any], int]:
    """Delete mod (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))

    db.delete(mod)
    db.commit()

    return {'error': False}, 200

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/background", methods=['POST'])
@with_session
@json_output
@user_required
def update_mod_background_new(game_id: int, category_stub: str, mod_id: int) -> Dict[str, Any]:
    """Update mod background (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    old_bg = mod.background
    path = _update_image(old_bg, mod.name, _cfg('storage'))
    if path:
        mod.background = path
        db.commit()
    return {'path': None}

# =============================================================================
# New API: Author Grant/Revoke
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/grant", methods=['POST'])
@with_session
@json_output
@user_required
def grant_mod_new(game_id: int, category_stub: str, mod_id: int) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Grant shared author (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    username = request.form.get('username')
    if not username:
        return {'error': True, 'reason': 'Missing username.'}
    user = User.query.filter(User.username == username).first()
    if not user:
        return {'error': True, 'reason': 'User does not exist.'}
    shared_author = SharedAuthor(user=user, mod=mod)
    db.add(shared_author)
    db.commit()
    send_grant_notice(mod, user)
    return {'error': False}

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/grant/accept", methods=['POST'])
@with_session
@json_output
@user_required
def accept_grant_new(game_id: int, category_stub: str, mod_id: int) -> Tuple[Dict[str, Any], int]:
    """Accept shared author grant (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    author = _get_mod_pending_author(mod)
    author.accepted = True
    db.commit()
    return {'error': False}, 200

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/grant/reject", methods=['POST'])
@with_session
@json_output
@user_required
def reject_grant_new(game_id: int, category_stub: str, mod_id: int) -> Tuple[Dict[str, Any], int]:
    """Reject shared author grant (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    author = _get_mod_pending_author(mod)
    db.delete(author)
    db.commit()
    return {'error': False}, 200

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/revoke", methods=['POST'])
@with_session
@json_output
@user_required
def revoke_mod_new(game_id: int, category_stub: str, mod_id: int) -> Tuple[Dict[str, Any], int]:
    """Revoke shared author (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    username = request.form.get('username')
    author = next((a for a in mod.shared_authors if a.user.username == username), None)
    if author:
        db.delete(author)
        db.commit()
    return {'error': False}, 200

# =============================================================================
# New API: Default Version
# =============================================================================

@api.route("/api/game/<int:game_id>/<category_stub>/<int:mod_id>/version/<int:vid>/default", methods=['POST'])
@with_session
@json_output
@user_required
def set_default_version_new(game_id: int, category_stub: str, mod_id: int, vid: int) -> Tuple[Dict[str, Any], int]:
    """Set default version (new API structure)."""
    mod = _get_category_mod(category_stub, mod_id)
    _check_mod_editable(mod)
    if mod.game_id != game_id:
        abort(json_response({'error': True, 'reason': 'Mod not found for game.'}, 404))
    ver = ModVersion.query.filter_by(id=vid).first()
    if ver and ver.mod_id == mod_id:
        mod.default_version = ver
        db.commit()
    return {'error': False}, 200

# =============================================================================
# New API: Pack Management
# =============================================================================

@api.route("/api/game/<int:game_id>/pack", methods=['POST'])
@with_session
@json_output
@user_required
def create_pack_new(game_id: int) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Create new pack (new API structure)."""
    if not current_user.public:
        return {'error': True, 'reason': 'Profile not public.'}, 403
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        return {'error': True, 'reason': 'Missing name.'}, 400
    mod_list = ModList(name=name, description=description, game_id=game_id)
    mod_list.user = current_user
    db.add(mod_list)
    db.commit()
    return {'id': mod_list.id, 'name': mod_list.name}, 201

@api.route("/api/game/<int:game_id>/pack/<int:pack_id>", methods=['PUT'])
@with_session
@json_output
@user_required
def update_pack_new(game_id: int, pack_id: int) -> Tuple[Dict[str, Any], int]:
    """Update pack (new API structure)."""
    pack = ModList.query.filter_by(id=pack_id, game_id=game_id).first()
    if not pack:
        abort(json_response({'error': True, 'reason': 'Pack not found.'}, 404))
    if not check_pack_editable(pack):
        abort(json_response({'error': True, 'reason': 'Not your pack.'}, 403))

    name = request.form.get('name')
    if name:
        pack.name = name
    description = request.form.get('description')
    if description:
        pack.description = description

    db.commit()
    return {'id': pack.id, 'name': pack.name}, 200

@api.route("/api/game/<int:game_id>/pack/<int:pack_id>", methods=['DELETE'])
@with_session
@json_output
@user_required
def delete_pack_new(game_id: int, pack_id: int) -> Tuple[Dict[str, Any], int]:
    """Delete pack (new API structure)."""
    pack = ModList.query.filter_by(id=pack_id, game_id=game_id).first()
    if not pack:
        abort(json_response({'error': True, 'reason': 'Pack not found.'}, 404))
    if not check_pack_editable(pack):
        abort(json_response({'error': True, 'reason': 'Not your pack.'}, 403))

    db.delete(pack)
    db.commit()
    return {'error': False}, 200

@api.route("/api/game/<int:game_id>/pack/<int:pack_id>/background", methods=['POST'])
@with_session
@json_output
@user_required
def update_pack_background_new(game_id: int, pack_id: int) -> Dict[str, Any]:
    """Update pack background (new API structure)."""
    pack = ModList.query.filter_by(id=pack_id, game_id=game_id).first()
    if not pack:
        abort(json_response({'error': True, 'reason': 'Pack not found.'}, 404))
    if not check_pack_editable(pack):
        abort(json_response({'error': True, 'reason': 'Not your pack.'}, 403))
    old_bg = pack.background
    path = _update_image(old_bg, pack.name, _cfg('storage'))
    if path:
        pack.background = path
        db.commit()
    return {'path': None}
# =============================================================================
# Additional Legacy Redirect Routes
# =============================================================================

@api.route("/api/kspversions")
@json_output
def legacy_kspversions_redirect() -> List[Dict[str, Any]]:
    """Legacy route: redirect to KSP versions list (game 1)."""
    return gameversions_list(1)

@api.route("/api/<game_id>/versions")
@json_output
def legacy_gameversions_list(game_id: int) -> List[Dict[str, Any]]:
    """Legacy route: redirect to new game versions list."""
    return gameversions_list(game_id)

@api.route("/api/<game_id>/categories")
@json_output
def legacy_gamecategories_list(game_id: int) -> List[Dict[str, Any]]:
    """Legacy route: redirect to new game categories list."""
    return gamecategories_list(game_id)

@api.route("/api/<game_id>/notifications")
@json_output
def legacy_game_notifications_list(game_id: int) -> List[Dict[str, Any]]:
    """Legacy route: redirect to new game notifications list."""
    return game_notifications_list(game_id)

@api.route("/api/browse")
@json_output
def legacy_browse_redirect() -> Dict[str, Any]:
    """Legacy route: redirect to browse with default game/category."""
    game_id = request.args.get('game_id', '1')
    return browse(game_id, 'all')

@api.route("/api/browse/new")
@json_output
def legacy_browse_new_redirect() -> Iterable[Dict[str, Any]]:
    """Legacy route: redirect to browse new with default game/category."""
    game_id = request.args.get('game_id', '1')
    return browse_new(game_id, 'all')

@api.route("/api/browse/top")
@json_output
def legacy_browse_top_redirect() -> Iterable[Dict[str, Any]]:
    """Legacy route: redirect to browse top with default game/category."""
    game_id = request.args.get('game_id', '1')
    return browse_top(game_id, 'all')

@api.route("/api/browse/featured")
@json_output
def legacy_browse_featured_redirect() -> Iterable[Dict[str, Any]]:
    """Legacy route: redirect to browse featured with default game/category."""
    game_id = request.args.get('game_id', '1')
    return browse_featured(game_id, 'all')

@api.route("/api/typeahead/mod")
@json_output
def legacy_typeahead_mod_redirect() -> Iterable[Dict[str, Any]]:
    """Legacy route: redirect to typeahead search with default game/category."""
    game_id = request.args.get('game_id', '1')
    return typeahead_mod(game_id, 'all')

@api.route("/api/search/mod")
@json_output
def legacy_search_mod_redirect() -> Iterable[Dict[str, Any]]:
    """Legacy route: redirect to mod search with default game/category."""
    game_id = request.args.get('game_id', '1')
    return search_mod(game_id, 'all')

@api.route("/api/login", methods=['POST'])
@json_output
def legacy_login_redirect() -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Legacy route: redirect to new login endpoint."""
    return login()

@api.route("/api/<game_id>/update-bg", methods=['POST'])
@with_session
@json_output
@user_required
def legacy_game_update_bg_redirect(game_id: int) -> Dict[str, Any]:
    """Legacy route: redirect to game background update."""
    return update_game_background(game_id)

@api.route("/api/user/<username>/change-password", methods=['POST'])
@with_session
@json_output
@user_required
def legacy_change_password_redirect(username: str) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Legacy route: redirect to password change."""
    return change_password(username)


# =============================================================================
# Pack Routes
# =============================================================================

@api.route('/api/pack/<int:pack_id>/update-bg', methods=['POST'])
@with_session
@json_output
@user_required
def update_pack_background(pack_id: int) -> Dict[str, Any]:
    pack = ModList.query.get(pack_id)
    if not pack:
        abort(json_response({'error': True, 'reason': 'Pack not found.'}, 404))
    if not check_pack_editable(pack):
        abort(json_response({'error': True, 'reason': 'Not your pack.'}, 403))
    old_bg = pack.background
    path = _update_image(old_bg, pack.name, _cfg('storage'))
    if path:
        pack.background = path
        db.commit()
    return {'path': None}