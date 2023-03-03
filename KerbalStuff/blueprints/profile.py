import re
from typing import Union
from itertools import groupby

import werkzeug.wrappers
from flask import Blueprint, render_template, abort, request, redirect
from flask_login import current_user

from .login_oauth import list_connected_oauths, list_defined_oauths
from ..common import loginrequired, with_session, sendfile, TRUE_STR
from ..config import _cfg
from ..objects import User, Following

profiles = Blueprint('profile', __name__)

FORUM_PROFILE_URL_PATTERN = re.compile(
    r'^(?P<prefix>https?://)?forum.kerbalspaceprogram.com/index.php\?/profile/(?P<id>[0-9]+)-(?P<name>[^/]+)')


@profiles.route("/profile/<username>")
def view_profile(username: str) -> str:
    profile = User.query.filter(User.username == username).first()
    if not profile:
        abort(404)
    if not profile.public:
        if not current_user:
            abort(401)
        if current_user.username != profile.username:
            if not current_user.admin:
                abort(403)
    forum_url_username = None
    forum_url = None
    match = FORUM_PROFILE_URL_PATTERN.match(profile.forumUsername)
    if match:
        forum_url_username = match.group('name')
        forum_url = (re.sub('^http://', 'https://', profile.forumUsername)
                     if match.group('prefix') else
                     f'https://{profile.forumUsername}')
    show_unpublished = current_user and (current_user.id == profile.id or current_user.admin)
    # Get the mods grouped by game, as [(game1_name, [mod1, mod2, ...]), (game2_name, [...]), ...]
    # with the games sorted alphabetically and the mods sorted by age.
    mods_created = list(map(lambda grp: (grp[0], sorted(grp[1],
                                                        key=lambda m: m.created,
                                                        reverse=True)),
                            groupby(sorted(profile.all_mods if show_unpublished
                                           else filter(lambda m: m.published,
                                                       profile.all_mods),
                                           key=lambda m: m.game.name),
                                    lambda m: m.game.name)))
    mods_followed = sorted(profile.following, key=lambda mod: mod.created, reverse=True)
    return render_template("view_profile.html",
                           profile=profile, forum_url=forum_url, forum_url_username=forum_url_username,
                           background=profile.background_url(_cfg('protocol'), _cfg('cdn-domain')),
                           mods_created=mods_created, mods_followed=mods_followed)


@profiles.route("/profile/<username>/background")
def profile_background(username: str) -> werkzeug.wrappers.Response:
    profile = User.query.filter(User.username == username).first()
    if not profile:
        abort(404)
    if not profile.public:
        if not current_user:
            abort(401)
        if current_user.username != profile.username:
            if not current_user.admin:
                abort(403)

    if not profile.backgroundMedia:
        # This won't happen for profile pages, as User.background_url() only redirects here if User.backgroundMedia is set.
        # However, it's possible that someone calls this manually.
        abort(404)

    return sendfile(profile.backgroundMedia, False)


@profiles.route("/profile/<username>/edit", methods=['GET', 'POST'])
@loginrequired
@with_session
def profile(username: str) -> Union[str, werkzeug.wrappers.Response]:
    if request.method == 'GET':
        profile = User.query.filter(User.username == username).first()
        if not profile:
            abort(404)
        if current_user != profile and not current_user.admin:
            abort(403)

        extra_auths = list_connected_oauths(profile)
        oauth_providers = list_defined_oauths()
        for provider in oauth_providers:
            oauth_providers[provider]['has_auth'] = provider in extra_auths

        following = sorted(Following.query.filter(Following.user_id == profile.id),
                           key=lambda fol: fol.mod.name.lower())

        parameters = {
            'profile': profile,
            'oauth_providers': oauth_providers,
            'hide_login': current_user != profile,
            'following': following,
            'background': profile.background_url(_cfg('protocol'), _cfg('cdn-domain')),
        }
        return render_template("profile.html", **parameters)
    else:
        profile = User.query.filter(User.username == username).first()
        if not profile:
            abort(404)
        if current_user != profile and not current_user.admin:
            abort(403)
        descr = request.form.get('description', '')
        if descr and len(descr) > 10000:
            abort(400)
        for key in ['ksp-forum-user', 'kerbalx', 'github', 'twitter', 'reddit', 'irc-nick']:
            val = request.form.get(key, '')
            if val and len(val) > 128:
                abort(400)
        profile.description = descr
        profile.forumUsername = request.form.get('ksp-forum-user')
        if profile.forumUsername:
            match = FORUM_PROFILE_URL_PATTERN.match(profile.forumUsername)
            if match:
                profile.forumId = match.group('id')
        profile.kerbalxUsername = request.form.get('kerbalx')
        profile.githubUsername = request.form.get('github')
        profile.twitterUsername = request.form.get('twitter')
        profile.redditUsername = request.form.get('reddit')
        profile.ircNick = request.form.get('irc-nick')
        bgOffsetX = request.form.get('bg-offset-x')
        bgOffsetY = request.form.get('bg-offset-y')
        profile.dark_theme = False
        if bgOffsetX:
            profile.bgOffsetX = int(bgOffsetX)
        if bgOffsetY:
            profile.bgOffsetY = int(bgOffsetY)
        for fol in Following.query.filter(Following.user_id == profile.id):
            fol.send_update = request.form.get(f'updates-{fol.mod_id}', '') in TRUE_STR
            fol.send_autoupdate = request.form.get(f'autoupdates-{fol.mod_id}', '') in TRUE_STR
        return redirect("/profile/" + profile.username)


@profiles.route("/profile/<username>/make-public", methods=['POST'])
@loginrequired
@with_session
def make_public(username: str) -> werkzeug.wrappers.Response:
    if current_user.username != username:
        abort(403)
    current_user.public = True
    return redirect("/profile/" + current_user.username)
