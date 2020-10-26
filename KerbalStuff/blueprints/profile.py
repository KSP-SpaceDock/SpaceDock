from flask import Blueprint, render_template, abort, request, redirect
from flask_login import current_user
import re
from typing import Union
import werkzeug.wrappers

from .login_oauth import list_connected_oauths, list_defined_oauths
from ..common import loginrequired, with_session
from ..objects import User

profiles = Blueprint('profile', __name__, template_folder='../../templates/profiles')

FORUM_PROFILE_URL_PATTERN = re.compile(
    '^https://forum.kerbalspaceprogram.com/index.php\?/profile/([0-9]+)-(.+)/$')

@profiles.route("/profile/<username>")
def view_profile(username: str) -> str:
    user = User.query.filter(User.username == username).first()
    if not user:
        abort(404)
    if not user.public:
        if not current_user:
            abort(401)
        if current_user.username != user.username:
            if not current_user.admin:
                abort(401)
    match = FORUM_PROFILE_URL_PATTERN.match(user.forumUsername)
    forum_url_username = match.groups()[1] if match else None
    mods_created = sorted(user.mods, key=lambda mod: mod.created, reverse=True)
    # Remove unpublished mods from the list if it's not the accessing's user's own profile, or it is and admin.
    if not current_user or (current_user.id != user.id and not current_user.admin):
        mods_created = [mod for mod in mods_created if mod.published]
    mods_followed = sorted(user.following, key=lambda mod: mod.created, reverse=True)
    return render_template("view_profile.html", profile=user, forum_url_username=forum_url_username, mods_created=mods_created, mods_followed=mods_followed)


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

        parameters = {
            'profile': profile,
            'oauth_providers': oauth_providers,
            'hide_login': current_user != profile
        }
        return render_template("profile.html", **parameters)
    else:
        profile = User.query.filter(User.username == username).first()
        if not profile:
            abort(404)
        if current_user != profile and not current_user.admin:
            abort(403)
        profile.redditUsername = request.form.get('reddit-username')
        profile.description = request.form.get('description')
        profile.twitterUsername = request.form.get('twitter')
        profile.forumUsername = request.form.get('ksp-forum-user')
        if profile.forumUsername:
            match = FORUM_PROFILE_URL_PATTERN.match(profile.forumUsername)
            if match:
                profile.forumId = match.groups()[0]
        profile.ircNick = request.form.get('irc-nick')
        profile.backgroundMedia = request.form.get('backgroundMedia')
        bgOffsetX = request.form.get('bg-offset-x')
        bgOffsetY = request.form.get('bg-offset-y')
        profile.dark_theme = False
        if bgOffsetX:
            profile.bgOffsetX = int(bgOffsetX)
        if bgOffsetY:
            profile.bgOffsetY = int(bgOffsetY)
        return redirect("/profile/" + profile.username)


@profiles.route("/profile/<username>/make-public", methods=['POST'])
@loginrequired
@with_session
def make_public(username: str) -> werkzeug.wrappers.Response:
    if current_user.username != username:
        abort(401)
    current_user.public = True
    return redirect("/profile/" + current_user.username)
