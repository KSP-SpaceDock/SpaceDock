from flask import Blueprint, render_template, abort, request, redirect, session, url_for, current_app, make_response, jsonify
from flask.ext.login import current_user, login_user
from sqlalchemy import desc, asc
from SpaceDock.search import search_mods, search_users, typeahead_mods
from SpaceDock.objects import *
from SpaceDock.common import *
from SpaceDock.config import _cfg
from SpaceDock.email import send_update_notification, send_grant_notice
from datetime import datetime

import time
import os
import zipfile
import urllib
import math
import json

api = Blueprint('api', __name__)

default_description = """This is your mod listing! You can edit it as much as you like before you make it public.

To edit **this** text, you can click on the "**Edit this Mod**" button up there.

By the way, you have a lot of flexibility here. You can embed YouTube videos or screenshots. Be creative.

You can check out the SpaceDock [markdown documentation](/markdown) for tips.

Thanks for hosting your mod on SpaceDock!"""

#some helper functions to keep things consistant
def user_info(user):
    return {
        "username": user.username,
        "description": user.description,
        "forumUsername": user.forumUsername,
        "ircNick": user.ircNick,
        "twitterUsername": user.twitterUsername,
        "redditUsername": user.redditUsername
    }

def mod_info(mod):
    return {
        "name": mod.name,
        "id": mod.id,
        "game": mod.game.name,
        "game_id": mod.game_id,
        "short_description": mod.short_description,
        "downloads": mod.download_count,
        "followers": mod.follower_count,
        "author": mod.user.username,
        "default_version_id": mod.default_version().id,
        "shared_authors": list(),
        "background": mod.background,
        "bg_offset_y": mod.bgOffsetY,
        "license": mod.license,
        "website": mod.external_link,
        "donations": mod.donation_link,
        "source_code": mod.source_link,
        "url": url_for("mods.mod", id=mod.id, mod_name=mod.name)
    }

def version_info(mod, version):
    return {
        "friendly_version": version.friendly_version,
        "game_version": version.gameversion.friendly_version,
        "id": version.id,
        "download_path": url_for('mods.download', mod_id=mod.id,
                                 mod_name=mod.name,
                                 version=version.friendly_version),
        "changelog": version.changelog
    }

def kspversion_info(version):
    return {
        "id": version.id,
        "friendly_version": version.friendly_version
    }

def game_info(game):
    return {
        "id": game.id,
        "name": game.name,
        "publisher_id": game.publisher_id,
        "short_description": game.short_description,
        "description": game.description,
        "created": game.created.isoformat(),
        "background": game.background,
        "bg_offset_x": game.bgOffsetX,
        "bg_offset_y": game.bgOffsetY,
        "link": game.link
    }

def publisher_info(publisher):
    return {
        "id": publisher.id,
        "name": publisher.name,
        "short_description": publisher.short_description,
        "description": publisher.description,
        "created": publisher.created,
        "background": publisher.background,
        "bg_offset_x": publisher.bgOffsetX,
        "bg_offset_y": publisher.bgOffsetY,
        "link": publisher.link
    }

@api.route("/api/kspversions")
@json_output
def kspversions_list():
    results = list()
    for v in GameVersion.query.order_by(desc(GameVersion.id)).all():
        results.append(kspversion_info(v))
    return results

@api.route("/api/<gameid>/versions")
@json_output
def gameversions_list(gameid):
    results = list()
    for v in GameVersion.query.filter(GameVersion.game_id == gameid).order_by(desc(GameVersion.id)).all():
        results.append(kspversion_info(v))

    return results

@api.route("/api/games")
@json_output
def games_list():
    results = list()
    for v in Game.query.order_by(desc(Game.name)).all():
        results.append(game_info(v))
	# Workaround because CustomJSONEncoder seems to have problems with this
    return json.dumps(results)

@api.route("/api/publishers")
@json_output
def publishers_list():
    results = list()
    for v in Publisher.query.order_by(desc(Publisher.id)).all():
        results.append(publisher_info(v))
    return results

@api.route("/api/typeahead/mod")
@json_output
def typeahead_mod():
    query = request.args.get('query')
    page = request.args.get('page')
    query = '' if not query else query
    page = 1 if not page or not page.isdigit() else int(page)
    results = list()
    for m in typeahead_mods(query):
        a = mod_info(m)
        a['versions'] = list()
        for v in m.versions:
            a['versions'].append(version_info(m, v))
        results.append(a)
    return results

@api.route("/api/search/mod")
@json_output
def search_mod():
    query = request.args.get('query')
    page = request.args.get('page')
    query = '' if not query else query
    page = 1 if not page or not page.isdigit() else int(page)
    results = list()
    for m in search_mods(False,query, page, 30)[0]:
        a = mod_info(m)
        a['versions'] = list()
        for v in m.versions:
            a['versions'].append(version_info(m, v))
        results.append(a)
    return results

@api.route("/api/search/user")
@json_output
def search_user():
    query = request.args.get('query')
    page = request.args.get('page')
    query = '' if not query else query
    page = 0 if not page or not page.isdigit() else int(page)
    results = list()
    for u in search_users(query, page):
        a = user_info(u)
        a['mods'] = list()
        mods = Mod.query.filter(Mod.user == u, Mod.published == True).order_by(Mod.created)
        for m in mods:
            a['mods'].append(mod_info(m))
        results.append(a)
    return results

@api.route("/api/browse")
@json_output
def browse():
    # set count per page
    count = request.args.get('count')
    count = 30 if not count or not count.isdigit() or int(count) > 500 else int(count)
    mods = Mod.query.filter(Mod.published)
    # detect total pages
    total_pages = math.ceil(mods.count() / count)
    total_pages = 1 if not total_pages > 0 else total_pages
    # order by field
    orderby = request.args.get('orderby')
    if orderby == "name":
        orderby = Mod.name
    elif orderby == "updated":
        orderby = Mod.updated
    else:
        orderby = Mod.created
    # order direction
    order = request.args.get('order')
    if order == "desc":
        mods.order_by(desc(orderby))
    else:
        mods.order_by(asc(orderby))
    # current page
    page = request.args.get('page')
    page = 1 if not page or not page.isdigit() or int(page) > total_pages else int(page)
    mods = mods.offset(count * (page - 1)).limit(count)
    # generate result
    results = list()
    for m in mods:
        a = mod_info(m)
        a['versions'] = list()
        for v in m.versions:
            a['versions'].append(version_info(m, v))
        results.append(a)
    return {
        "count": count,
        "pages": total_pages,
        "page": page,
        "result": results
    }

@api.route("/api/browse/new")
@json_output
def browse_new():
    mods = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    page = 1 if not page or not page.isdigit() else int(page)
    if page:
        page = int(page)
        if page > total_pages:
            page = total_pages
        if page < 1:
            page = 1
    else:
        page = 1
    mods = mods.offset(30 * (page - 1)).limit(30)
    results = list()
    for m in mods:
        a = mod_info(m)
        a['versions'] = list()
        for v in m.versions:
            a['versions'].append(version_info(m, v))
        results.append(a)
    return results

@api.route("/api/browse/top")
@json_output
def browse_top():
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(False,"", page, 30)
    results = list()
    for m in mods:
        a = mod_info(m)
        a['versions'] = list()
        for v in m.versions:
            a['versions'].append(version_info(m, v))
        results.append(a)
    return results

@api.route("/api/browse/featured")
@json_output
def browse_featured():
    mods = Featured.query.order_by(desc(Featured.created))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    if page != 0:
        mods = mods.offset(30 * (page - 1)).limit(30)
    mods = [f.mod for f in mods]
    results = list()
    for m in mods:
        a = mod_info(m)
        a['versions'] = list()
        for v in m.versions:
            a['versions'].append(version_info(m, v))
        results.append(a)
    return results

@api.route("/api/login", methods=['POST'])
@json_output
def login():
    username = request.form['username']
    password = request.form['password']
    if not username or not password:
        return { 'error': True, 'reason': 'Missing username or password' }, 400
    user = User.query.filter(User.username.ilike(username)).first()
    if not user:
        return { 'error': True, 'reason': 'Username or password is incorrect' }, 400
    if not bcrypt.hashpw(password.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
        return { 'error': True, 'reason': 'Username or password is incorrect' }, 400
    if user.confirmation != '' and user.confirmation != None:
        return { 'error': True, 'reason': 'User is not confirmed' }, 400
    login_user(user)
    return { 'error': False }

@api.route("/api/mod/<modid>")
@json_output
def mod(modid):
    if not modid.isdigit():
       return { 'error': True, 'reason': 'Invalid mod ID.' }, 400
    mod = Mod.query.filter(Mod.id == modid).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    if not mod.published:
        return { 'error': True, 'reason': 'Mod not published.' }, 401
    info = mod_info(mod)
    info["versions"] = list()
    for author in mod.sharedauthor:
        info["shared_authors"].append(user_info(author.user))
    for v in mod.versions:
        info["versions"].append(version_info(mod, v))
    info["description"] = mod.description
    info["description_html"] = str(current_app.jinja_env.filters['markdown'](mod.description))
    return info

@api.route("/api/mod/<modid>/<version>")
@json_output
def mod_version(modid, version):
    if not modid.isdigit():
        return { 'error': True, 'reason': 'Invalid mod ID.' }, 400
    mod = Mod.query.filter(Mod.id == modid).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    if not mod.published:
        return { 'error': True, 'reason': 'Mod not published.' }, 401
    if version == "latest" or version == "latest_version":
        v = mod.default_version()
    elif version.isdigit():
        v = ModVersion.query.filter(ModVersion.mod == mod,
                                    ModVersion.id == int(version)).first()
    else:
        return { 'error': True, 'reason': 'Invalid version.' }, 400
    if not v:
        return { 'error': True, 'reason': 'Version not found.' }, 404
    info = version_info(mod, v)
    return info

@api.route("/api/user/<username>")
@json_output
def user(username):
    user = User.query.filter(User.username == username).first()
    if not user:
        return { 'error': True, 'reason': 'User not found.' }, 404
    if not user.public:
        return { 'error': True, 'reason': 'User not public.' }, 401
    mods = Mod.query.filter(Mod.user == user, Mod.published == True).order_by(
        Mod.created)
    info = user_info(user)
    info['mods'] = list()
    for m in mods:
        info['mods'].append(mod_info(m))
    return info

@api.route('/api/mod/<mod_id>/update-bg', methods=['POST'])
@with_session
@json_output
def update_mod_background(mod_id):
    if current_user == None:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
        if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
            editable = True
    if not editable:
        return { 'error': True, 'reason': 'Not enought rights.' }, 401
    f = request.files['image']
    filetype = os.path.splitext(os.path.basename(f.filename))[1]
    if not filetype in ['.png', '.jpg']:
        return { 'error': True, 'reason': 'This file type is not acceptable.' }, 400
    filename = secure_filename(mod.name) + '-' + str(time.time()) + filetype
    base_path = os.path.join(secure_filename(mod.user.username) + '_' + str(mod.user.id), secure_filename(mod.name))
    full_path = os.path.join(_cfg('storage'), base_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    path = os.path.join(full_path, filename)
    try:
        os.remove(os.path.join(_cfg('storage'), mod.background))
    except:
        pass # who cares
    f.save(path)
    mod.background = os.path.join(base_path, filename)
    return { 'path': '/content/' + mod.background }

@api.route('/api/user/<username>/update-bg', methods=['POST'])
@with_session
@json_output
def update_user_background(username):
    if current_user == None:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    user = User.query.filter(User.username == username).first()
    if not current_user.admin and current_user.username != user.username:
        return { 'error': True, 'reason': 'You are not authorized to edit this user\'s background' }, 403
    f = request.files['image']
    filetype = os.path.splitext(os.path.basename(f.filename))[1]
    if not filetype in ['.png', '.jpg']:
        return { 'error': True, 'reason': 'This file type is not acceptable.' }, 400
    filename = secure_filename(user.username) + filetype
    base_path = os.path.join(secure_filename(user.username) + '-' + str(time.time()) + '_' + str(user.id))
    full_path = os.path.join(_cfg('storage'), base_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    path = os.path.join(full_path, filename)
    try:
        os.remove(os.path.join(_cfg('storage'), user.backgroundMedia))
    except:
        pass # who cares
    f.save(path)
    user.backgroundMedia = os.path.join(base_path, filename)
    return { 'path': '/content/' + user.backgroundMedia }

@api.route('/api/mod/<mod_id>/grant', methods=['POST'])
@with_session
@json_output
def grant_mod(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
    if not editable:
        return { 'error': True, 'reason': 'Not enought rights.' }, 401
    new_user = request.form.get('user')
    new_user = User.query.filter(User.username.ilike(new_user)).first()
    if new_user == None:
        return { 'error': True, 'reason': 'The specified user does not exist.' }, 400
    if mod.user == new_user:
        return { 'error': True, 'reason': 'This user has already been added.' }, 400
    if any(m.user == new_user for m in mod.shared_authors):
        return { 'error': True, 'reason': 'This user has already been added.' }, 400
    if not new_user.public:
        return { 'error': True, 'reason': 'This user has not made their profile public.' }, 400
    author = SharedAuthor()
    author.mod = mod
    author.user = new_user
    mod.shared_authors.append(author)
    db.add(author)
    db.commit()
    send_grant_notice(mod, new_user)
    return { 'error': False }, 200

@api.route('/api/mod/<mod_id>/accept_grant', methods=['POST'])
@with_session
@json_output
def accept_grant_mod(mod_id):
    if current_user == None:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    author = [a for a in mod.shared_authors if a.user == current_user]
    if len(author) == 0:
        return { 'error': True, 'reason': 'You do not have a pending authorship invite.' }, 200
    author = author[0]
    if author.accepted:
        return { 'error': True, 'reason': 'You do not have a pending authorship invite.' }, 200
    author.accepted = True
    return { 'error': False }, 200

@api.route('/api/mod/<mod_id>/reject_grant', methods=['POST'])
@with_session
@json_output
def reject_grant_mod(mod_id):
    if current_user == None:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    author = [a for a in mod.shared_authors if a.user == current_user]
    if len(author) == 0:
        return { 'error': True, 'reason': 'You do not have a pending authorship invite.' }, 200
    author = author[0]
    if author.accepted:
        return { 'error': True, 'reason': 'You do not have a pending authorship invite.' }, 200
    mod.shared_authors = [a for a in mod.shared_authors if a.user != current_user]
    db.delete(author)
    return { 'error': False }, 200

@api.route('/api/mod/<mod_id>/revoke', methods=['POST'])
@with_session
@json_output
def revoke_mod(mod_id):
    if current_user == None:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
    if not editable:
        return { 'error': True, 'reason': 'Not enought rights.' }, 401
    new_user = request.form.get('user')
    new_user = User.query.filter(User.username.ilike(new_user)).first()
    if new_user == None:
        return { 'error': True, 'reason': 'The specified user does not exist.' }, 404
    if mod.user == new_user:
        return { 'error': True, 'reason': 'You can\'t remove yourself.' }, 400
    if not any(m.user == new_user for m in mod.shared_authors):
        return { 'error': True, 'reason': 'This user is not an author.' }, 400
    author = [a for a in mod.shared_authors if a.user == new_user][0]
    mod.shared_authors = [a for a in mod.shared_authors if a.user != current_user]
    db.delete(author)
    return { 'error': False }, 200

@api.route('/api/mod/<int:mid>/set-default/<int:vid>', methods=['POST'])
@with_session
@json_output
def set_default_version(mid, vid):
    mod = Mod.query.filter(Mod.id == mid).first()
    if not mod:
        return { 'error': True, 'reason': 'The specified mod does not exist.' }, 404
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
        if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
            editable = True
    if not editable:
        return { 'error': True, 'reason': 'You do not have permission to do this.' }, 400
    if not any([v.id == vid for v in mod.versions]):
        return { 'error': True, 'reason': 'This mod does not have the specified version.' }, 404
    mod.default_version_id = vid
    return { 'error': False }, 200

@api.route('/api/pack/create', methods=['POST'])
@json_output
@with_session
def create_list():
    if not current_user:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    if not current_user.public:
        return { 'error': True, 'reason': 'Only users with public profiles may create mod packs.' }, 403
    name = request.form.get('name')
    if not name:
        return { 'error': True, 'reason': 'All fields are required.' }, 400
    game = request.form.get('game')
    if not game:
        return {'error': True, 'reason': 'Please select a game.'}, 400
    if len(name) > 100:
        return { 'error': True, 'reason': 'Fields exceed maximum permissible length.' }, 400
    mod_list = ModList()
    mod_list.name = name
    mod_list.user = current_user
    mod_list.game_id = game
    db.add(mod_list)
    db.commit()
    return { 'url': url_for("lists.view_list", list_id=mod_list.id, list_name=mod_list.name) }

@api.route('/api/mod/create', methods=['POST'])
@json_output
def create_mod():
    if not current_user:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    if not current_user.public:
        return { 'error': True, 'reason': 'Only users with public profiles may create mods.' }, 403
    name = request.form.get('name')
    game = request.form.get('game')
    short_description = request.form.get('short-description')
    version = request.form.get('version')
    game_version = request.form.get('game-version')
    license = request.form.get('license')
    ckan = request.form.get('ckan')
    zipball = request.files.get('zipball')
    # Validate
    if not name \
        or not short_description \
        or not version \
        or not game \
        or not game_version \
        or not license \
        or not zipball:
        return { 'error': True, 'reason': 'All fields are required.' }, 400
    # Validation, continued
    if len(name) > 100 \
        or len(short_description) > 1000 \
        or len(license) > 128:
        return { 'error': True, 'reason': 'Fields exceed maximum permissible length.' }, 400
    if ckan == None:
        ckan = False
    else:
        ckan = (ckan.lower() == "true" or ckan.lower() == "yes" or ckan.lower() == "on")
    test_game = Game.query.filter(Game.id == game).first()
    if not test_game:
        return { 'error': True, 'reason': 'Game does not exist.' }, 400
    test_gameversion = GameVersion.query.filter(GameVersion.game_id == test_game.id).filter(GameVersion.friendly_version == game_version).first()
    if not test_gameversion:
        return { 'error': True, 'reason': 'Game version does not exist.' }, 400
    game_version_id = test_gameversion.id
    mod = Mod()
    mod.user = current_user
    mod.name = name
    mod.game_id = game
    mod.short_description = short_description
    mod.description = default_description
    mod.ckan = ckan
    mod.license = license
    # Save zipball
    filename = secure_filename(name) + '-' + secure_filename(version) + '.zip'
    base_path = os.path.join(secure_filename(current_user.username) + '_' + str(current_user.id), secure_filename(name))
    full_path = os.path.join(_cfg('storage'), base_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    path = os.path.join(full_path, filename)
    if os.path.isfile(path):
        # We already have this version
        # We'll remove it because the only reason it could be here on creation is an error
        os.remove(path)
    zipball.save(path)
    if not zipfile.is_zipfile(path):
        os.remove(path)
        return { 'error': True, 'reason': 'This is not a valid zip file.' }, 400
    version = ModVersion(secure_filename(version), game_version_id, os.path.join(base_path, filename))
    mod.versions.append(version)
    db.add(version)
    # Save database entry
    db.add(mod)
    db.commit()
    mod.default_version_id = version.id
    ga = Game.query.filter(Game.id == game).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    return { 'url': url_for("mods.mod", id=mod.id, mod_name=mod.name), "id": mod.id, "name": mod.name }

@api.route('/api/mod/<mod_id>/update', methods=['POST'])
@with_session
@json_output
def update_mod(mod_id):
    if current_user == None:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        return { 'error': True, 'reason': 'Mod not found.' }, 404
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
        if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
            editable = True
    if not editable:
        return { 'error': True, 'reason': 'Not enought rights.' }, 401
    version = request.form.get('version')
    changelog = request.form.get('changelog')
    game_version = request.form.get('game-version')
    notify = request.form.get('notify-followers')
    zipball = request.files.get('zipball')
    if not version \
        or not game_version \
        or not zipball:
        # Client side validation means that they're just being pricks if they
        # get here, so we don't need to show them a pretty error reason
        # SMILIE: this doesn't account for "external" API use --> return a json error
        return { 'error': True, 'reason': 'All fields are required.' }, 400
    test_gameversion = GameVersion.query.filter(GameVersion.game_id == Mod.game_id).filter(GameVersion.friendly_version == game_version).first()
    if not test_gameversion:
        return { 'error': True, 'reason': 'Game version does not exist.' }, 400
    game_version_id = test_gameversion.id
    if notify == None:
        notify = False
    else:
        notify = (notify.lower() == "true" or notify.lower() == "yes")
    filename = secure_filename(mod.name) + '-' + secure_filename(version) + '.zip'
    base_path = os.path.join(secure_filename(current_user.username) + '_' + str(current_user.id), secure_filename(mod.name))
    full_path = os.path.join(_cfg('storage'), base_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    path = os.path.join(full_path, filename)
    for v in mod.versions:
        if v.friendly_version == secure_filename(version):
            return { 'error': True, 'reason': 'We already have this version. Did you mistype the version number?' }, 400
    if os.path.isfile(path):
        os.remove(path)        
    zipball.save(path)
    if not zipfile.is_zipfile(path):
        os.remove(path)
        return { 'error': True, 'reason': 'This is not a valid zip file.' }, 400
    version = ModVersion(secure_filename(version), game_version_id, os.path.join(base_path, filename))
    version.changelog = changelog
    # Assign a sort index
    if len(mod.versions) == 0:
        version.sort_index = 0
    else:
        version.sort_index = max([v.sort_index for v in mod.versions]) + 1
    mod.versions.append(version)
    mod.updated = datetime.now()
    if notify:
        send_update_notification(mod, version, current_user)
    db.add(version)
    db.commit()
    mod.default_version_id = version.id
    return { 'url': url_for("mods.mod", id=mod.id, mod_name=mod.name), "id": version.id  }
