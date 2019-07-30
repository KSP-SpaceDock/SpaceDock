import os
import random
from datetime import datetime, timedelta
from shutil import rmtree
from urllib.parse import urlparse

from flask import Blueprint, render_template, send_file, make_response, url_for, session
from sqlalchemy import desc

from .api import default_description
from ..celery import notify_ckan
from ..ckan import send_to_ckan
from ..common import *
from ..config import _cfg
from ..email import send_autoupdate_notification
from ..objects import Mod, ModVersion, DownloadEvent, FollowEvent, ReferralEvent, \
    Featured, Media, GameVersion, Game

mods = Blueprint('mods', __name__, template_folder='../../templates/mods')

@mods.route("/random")
def random_mod():
    mods = None
    if session.get('gameid'):
        if session['gameid']:
            mods = Mod.query.filter(Mod.game_id == session['gameid']).filter(Mod.published == True).all()
    else:
        mods = Mod.query.filter(Mod.published == True).all()
    if not mods:
        abort(404)
    mod = random.choice(mods)
    return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name))

@mods.route("/mod/<int:id>/<path:mod_name>/update")
def update(id, mod_name):
    if session.get('gameid'):
        if session['gameid']:
            ga = Game.query.filter(Game.id == session['gameid']).order_by(desc(Game.id)).first()
        else:
            ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
    else:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
    session['game'] = ga.id
    session['gamename'] = ga.name
    session['gameshort'] = ga.short
    session['gameid'] = ga.id
    mod = Mod.query.filter(Mod.id == id, Mod.game_id == ga.id).first()
    if not mod or not ga:
        abort(404)
    editable = False
    if current_user.admin:
        editable = True
    if current_user.id == mod.user_id:
        editable = True
    if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
        editable = True
    if not editable:
        abort(401)
    return render_template("update.html", mod=mod, game_versions=GameVersion.query.filter(GameVersion.game_id == mod.game_id).order_by(desc(GameVersion.id)).all(),ga=ga)

@mods.route("/mod/<int:id>.rss", defaults={'mod_name': None})
@mods.route("/mod/<int:id>/<path:mod_name>.rss")
def mod_rss(id, mod_name):
    mod = Mod.query.filter(Mod.id == id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    if not mod or not game:
        abort(404)
    return render_template("rss-mod.xml", mod=mod,ga=game)

@mods.route("/mod/<int:id>", defaults={'mod_name': None})
@mods.route("/mod/<int:id>/<path:mod_name>")
@with_session
def mod(id, mod_name):
    ga = None
    mod = Mod.query.filter(Mod.id == id).first()
    if mod:
        ga = mod.game
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
    if not mod or not ga:
        abort(404)
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
    if not mod.published and not editable:
        abort(401)
    latest = mod.default_version()
    referral = request.referrer
    if referral:
        host = urllib.parse.urlparse(referral).hostname
        event = ReferralEvent.query\
                .filter(ReferralEvent.mod_id == mod.id)\
                .filter(ReferralEvent.host == host)\
                .first()
        if not event:
            event = ReferralEvent()
            event.mod = mod
            event.events = 1
            event.host = host
            db.add(event)
            db.flush()
            db.commit()
            mod.referrals.append(event)
        else:
            event.events += 1
    thirty_days_ago = datetime.now() - timedelta(days=30)
    referrals = list()
    for r in ReferralEvent.query\
        .filter(ReferralEvent.mod_id == mod.id)\
        .order_by(desc(ReferralEvent.events)):
        referrals.append( { 'host': r.host, 'count': r.events } )
    download_stats = list()
    for d in DownloadEvent.query\
        .filter(DownloadEvent.mod_id == mod.id)\
        .filter(DownloadEvent.created > thirty_days_ago)\
        .order_by(DownloadEvent.created):
        download_stats.append(dumb_object(d))
    follower_stats = list()
    for f in FollowEvent.query\
        .filter(FollowEvent.mod_id == mod.id)\
        .filter(FollowEvent.created > thirty_days_ago)\
        .order_by(FollowEvent.created):
        follower_stats.append(dumb_object(f))
    json_versions = list()
    for v in mod.versions:
        json_versions.append({ 'name': v.friendly_version, 'id': v.id })
    if request.args.get('noedit') is not None:
        editable = False
    forumThread = False
    if mod.external_link is not None:
        try:
            u = urlparse(mod.external_link)
            if u.netloc == 'forum.kerbalspaceprogram.com':
                forumThread = True
        except Exception as e:
            print(e)
            pass
    total_authors = 1
    pending_invite = False
    owner = editable
    for a in mod.shared_authors:
        if a.accepted:
            total_authors += 1
        if current_user:
            if current_user.id == a.user_id and not a.accepted:
                pending_invite = True
            if current_user.id == a.user_id and a.accepted:
                editable = True
    games = Game.query.filter(Game.active == True).order_by(desc(Game.id)).all()

    game_versions = GameVersion.query.filter(GameVersion.game_id == mod.game_id).order_by(desc(GameVersion.id)).all()

    outdated = False
    if latest:
        outdated = latest.gameversion.id != game_versions[0].id and latest.gameversion.friendly_version != '1.0.5'
    return render_template("mod.html",
        **{
            'mod': mod,
            'latest': latest,
            'safe_name': secure_filename(mod.name)[:64],
            'featured': any(Featured.query.filter(Featured.mod_id == mod.id).all()),
            'editable': editable,
            'owner': owner,
            'pending_invite': pending_invite,
            'download_stats': download_stats,
            'follower_stats': follower_stats,
            'referrals': referrals,
            'json_versions': json_versions,
            'thirty_days_ago': thirty_days_ago,
            'share_link': urllib.parse.quote_plus(_cfg("protocol") + "://" + _cfg("domain") + "/mod/" + str(mod.id)),
            'game_versions': game_versions,
            'games':  games,
            'outdated': outdated,
            'forum_thread': forumThread,
            'new': request.args.get('new') is not None,
            'stupid_user': request.args.get('stupid_user') is not None,
            'total_authors': total_authors,
            "site_name": _cfg('site-name'),
            "support_mail": _cfg('support-mail'),
            'ga': ga
        })

@mods.route("/mod/<int:id>/<path:mod_name>/edit", methods=['GET', 'POST'])
@with_session
@loginrequired
def edit_mod(id, mod_name):
    mod = Mod.query.filter(Mod.id == id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    if not mod or not game:
        abort(404)
    editable = False
    if current_user.admin:
        editable = True
    if current_user.id == mod.user_id:
        editable = True
    if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
        editable = True
    if not editable:
        abort(401)
    if request.method == 'GET':
        return render_template("edit_mod.html", mod=mod, original=mod.user == current_user)
    else:
        short_description = request.form.get('short-description')
        license = request.form.get('license')
        donation_link = request.form.get('donation-link')
        external_link = request.form.get('external-link')
        source_link = request.form.get('source-link')
        description = request.form.get('description')
        ckan = request.form.get('ckan')
        background = request.form.get('background')
        bgOffsetY = request.form.get('bg-offset-y')
        if not license or license == '':
            return render_template("edit_mod.html", mod=mod, error="All mods must have a license.")
        if ckan is None:
            ckan = False
        else:
            ckan = (ckan.lower() == "true" or ckan.lower() == "yes" or ckan.lower() == "on")
        mod.short_description = short_description
        mod.license = license
        mod.donation_link = donation_link
        mod.external_link = external_link
        mod.source_link = source_link
        mod.description = description
        if not mod.ckan and ckan:
            mod.ckan = ckan
            if mod.published:
                send_to_ckan(mod)
        if background and background != '':
            mod.background = background
        try:
            mod.bgOffsetY = int(bgOffsetY)
        except:
            pass
        return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name,ga=game))

@mods.route("/create/mod")
@loginrequired
@with_session
def create_mod():
    games = Game.query.filter(Game.active == True).order_by(desc(Game.id)).all()
    if session.get('gameid'):
        if session['gameid']:
            ga = Game.query.filter(Game.id == session['gameid']).order_by(desc(Game.id)).first()
        else:
            ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
    else:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
    session['game'] = ga.id
    session['gamename'] = ga.name
    session['gameshort'] = ga.short
    session['gameid'] = ga.id
    game_versions = GameVersion.query.filter(GameVersion.game_id == ga.id).order_by(desc(GameVersion.id)).all()
    return render_template("create.html", game_versions=game_versions,game=games,ga=ga)

@mods.route("/mod/<int:mod_id>/stats/downloads", defaults={'mod_name': None})
@mods.route("/mod/<int:mod_id>/<path:mod_name>/stats/downloads")
def export_downloads(mod_id, mod_name):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    if not mod or not game:
        abort(404)
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    download_stats = DownloadEvent.query\
        .filter(DownloadEvent.mod_id == mod.id)\
        .order_by(DownloadEvent.created)
    response = make_response(render_template("downloads.csv", stats=download_stats))
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment;filename=downloads.csv'
    return response

@mods.route("/mod/<int:mod_id>/stats/followers", defaults={'mod_name': None})
@mods.route("/mod/<int:mod_id>/<path:mod_name>/stats/followers")
def export_followers(mod_id, mod_name):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    if not mod or not game:
        abort(404)
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    follower_stats = FollowEvent.query\
        .filter(FollowEvent.mod_id == mod.id)\
        .order_by(FollowEvent.created)
    response = make_response(render_template("followers.csv", stats=follower_stats))
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment;filename=followers.csv'
    return response

@mods.route("/mod/<int:mod_id>/stats/referrals", defaults={'mod_name': None})
@mods.route("/mod/<mod_id>/<path:mod_name>/stats/referrals")
def export_referrals(mod_id, mod_name):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    if not game:
        abort(404)
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    referral_stats = ReferralEvent.query\
            .filter(ReferralEvent.mod_id == mod.id)\
            .order_by(desc(ReferralEvent.events))
    response = make_response(render_template("referrals.csv", stats=referral_stats))
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment;filename=referrals.csv'
    return response

@mods.route("/mod/<int:mod_id>/delete", methods=['POST'])
@loginrequired
@with_session
def delete(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
    if not editable:
        abort(401)
    db.delete(mod)
    for feature in Featured.query.filter(Featured.mod_id == mod.id).all():
        db.delete(feature)
    for media in Media.query.filter(Media.mod_id == mod.id).all():
        db.delete(media)
    for version in ModVersion.query.filter(ModVersion.mod_id == mod.id).all():
        db.delete(version)
    base_path = os.path.join(secure_filename(mod.user.username) + '_' + str(mod.user.id), secure_filename(mod.name))
    full_path = os.path.join(_cfg('storage'), base_path)
    db.commit()
    notify_ckan.delay(mod_id, 'delete')
    rmtree(full_path)
    return redirect("/profile/" + current_user.username)

@mods.route("/mod/<int:mod_id>/follow", methods=['POST'])
@loginrequired
@json_output
@with_session
def follow(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    if any(m.id == mod.id for m in current_user.following):
        abort(418)
    event = FollowEvent.query\
            .filter(FollowEvent.mod_id == mod.id)\
            .order_by(desc(FollowEvent.created))\
            .first()
    # Events are aggregated hourly
    if not event or ((datetime.now() - event.created).seconds / 60 / 60) >= 1:
        event = FollowEvent()
        event.mod = mod
        event.delta = 1
        event.events = 1
        db.add(event)
        db.flush()
        db.commit()
        mod.follow_events.append(event)
    else:
        event.delta += 1
        event.events += 1
    mod.follower_count += 1
    current_user.following.append(mod)
    return { "success": True }

@mods.route("/mod/<int:mod_id>/unfollow", methods=['POST'])
@loginrequired
@json_output
@with_session
def unfollow(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    if not any(m.id == mod.id for m in current_user.following):
        abort(418)
    event = FollowEvent.query\
            .filter(FollowEvent.mod_id == mod.id)\
            .order_by(desc(FollowEvent.created))\
            .first()
    # Events are aggregated hourly
    if not event or ((datetime.now() - event.created).seconds / 60 / 60) >= 1:
        event = FollowEvent()
        event.mod = mod
        event.delta = -1
        event.events = 1
        mod.follow_events.append(event)
        db.add(event)
    else:
        event.delta -= 1
        event.events += 1
    mod.follower_count -= 1
    current_user.following = [m for m in current_user.following if m.id != int(mod_id)]
    return { "success": True }

@mods.route('/mod/<int:mod_id>/feature', methods=['POST'])
@adminrequired
@json_output
@with_session
def feature(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    if any(Featured.query.filter(Featured.mod_id == mod_id).all()):
        abort(409)
    feature = Featured()
    feature.mod = mod
    db.add(feature)
    return { "success": True }

@mods.route('/mod/<mod_id>/unfeature', methods=['POST'])
@adminrequired
@json_output
@with_session
def unfeature(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    feature = Featured.query.filter(Featured.mod_id == mod_id).first()
    if not feature:
        abort(404)
    db.delete(feature)
    return { "success": True }

@mods.route('/mod/<int:mod_id>/<path:mod_name>/publish')
@with_session
@loginrequired
def publish(mod_id, mod_name):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    if current_user.id != mod.user_id:
        abort(401)
    if mod.description == default_description:
        return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name, stupid_user=True))
    mod.published = True
    mod.updated = datetime.now()
    send_to_ckan(mod)
    return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name))

@mods.route('/mod/<int:mod_id>/download/<version>', defaults={ 'mod_name': None })
@mods.route('/mod/<int:mod_id>/<path:mod_name>/download/<version>')
@with_session
def download(mod_id, mod_name, version):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    if not mod.published and (not current_user or current_user.id != mod.user_id):
        abort(401)
    version = ModVersion.query.filter(ModVersion.mod_id == mod_id,
                                      ModVersion.friendly_version == version).first()
    if not version:
        abort(404)
    download = DownloadEvent.query\
            .filter(DownloadEvent.mod_id == mod.id and DownloadEvent.version_id == version.id)\
            .order_by(desc(DownloadEvent.created))\
            .first()
    if not os.path.isfile(os.path.join(_cfg('storage'), version.download_path)):
        abort(404)

    if not 'Range' in request.headers:
        # Events are aggregated hourly
        if not download or ((datetime.now() - download.created).seconds / 60 / 60) >= 1:
            download = DownloadEvent()
            download.mod = mod
            download.version = version
            download.downloads = 1
            db.add(download)
            db.flush()
            db.commit()
            mod.downloads.append(download)
        else:
            download.downloads += 1
        mod.download_count += 1

    if _cfg("cdn-domain"):
        return redirect("http://" + _cfg("cdn-domain") + '/' + version.download_path, code=302)

    response = None
    if _cfg("use-x-accel") == 'nginx':
        response = make_response("")
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = 'attachment; filename=' + os.path.basename(version.download_path)
        response.headers['X-Accel-Redirect'] = '/internal/' + version.download_path
    if _cfg("use-x-accel") == 'apache':
        response = make_response("")
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = 'attachment; filename=' + os.path.basename(version.download_path)
        response.headers['X-Sendfile'] = os.path.join(_cfg('storage'), version.download_path)
    if response is None:
        response = make_response(send_file(os.path.join(_cfg('storage'), version.download_path), as_attachment = True))
    return response

@mods.route('/mod/<int:mod_id>/version/<version_id>/delete', methods=['POST'])
@with_session
@loginrequired
def delete_version(mod_id, version_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
        if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
            editable = True
    if not editable:
        abort(401)
    version = [v for v in mod.versions if v.id == int(version_id)]
    if len(mod.versions) == 1:
        abort(400)
    if len(version) == 0:
        abort(404)
    if version[0].id == mod.default_version_id:
        abort(400)
    db.delete(version[0])
    mod.versions = [v for v in mod.versions if v.id != int(version_id)]
    db.commit()
    return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name,ga=game))


@mods.route('/mod/<int:mod_id>/<mod_name>/edit_version', methods=['POST'])
@mods.route('/mod/<int:mod_id>/edit_version', methods=['POST'], defaults={ 'mod_name': None })
@with_session
@loginrequired
def edit_version(mod_name, mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    else:
        session['game'] = game.id
        session['gamename'] = game.name
        session['gameshort'] = game.short
        session['gameid'] = game.id
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
        if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
            editable = True
    if not editable:
        abort(401)
    version_id = int(request.form.get('version-id'))
    changelog = request.form.get('changelog')
    version = [v for v in mod.versions if v.id == version_id]
    if len(version) == 0:
        abort(404)
    version = version[0]
    version.changelog = changelog
    return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name,ga=game))

@mods.route('/mod/<int:mod_id>/autoupdate', methods=['POST'])
@with_session
@loginrequired
def autoupdate(mod_id):
    mod = Mod.query.filter(Mod.id == mod_id).first()
    if not mod:
        abort(404)
    game = Game.query.filter(Game.id == mod.game_id).first()
    session['game'] = game.id
    session['gamename'] = game.name
    session['gameshort'] = game.short
    session['gameid'] = game.id
    if not mod or not game:
        ga = Game.query.filter(Game.short == 'kerbal-space-program').order_by(desc(Game.id)).first()
        session['game'] = ga.id
        session['gamename'] = ga.name
        session['gameshort'] = ga.short
        session['gameid'] = ga.id
        abort(404)
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod.user_id:
            editable = True
        if any([u.accepted and u.user == current_user for u in mod.shared_authors]):
            editable = True
    if not editable:
        abort(401)
    default = mod.default_version()
    default.gameversion_id = GameVersion.query.filter(GameVersion.game_id == mod.game_id).order_by(desc(GameVersion.id)).first().id
    send_autoupdate_notification(mod)
    notify_ckan.delay(mod_id, 'version-update')
    return redirect(url_for("mods.mod", id=mod.id, mod_name=mod.name,ga=game))
