from flask import Blueprint, render_template, abort
from flask.ext.login import current_user
from SpaceDock.objects import User
from SpaceDock.database import db
from SpaceDock.common import *
from SpaceDock.config import _cfg
from SpaceDock.blueprints.login_oauth import list_connected_oauths, list_defined_oauths

profiles = Blueprint('profile', __name__, template_folder='../../templates/profiles')

@profiles.route("/profile/<username>")
def view_profile(username):
    user = User.query.filter(User.username == username).first()
    if not user:
        abort(404)
    if not user.public:
        if not current_user:
            abort(401)
        if current_user.username != user.username:
            if not current_user.admin:
                abort(401)
    mods_created = sorted(user.mods, key=lambda mod: mod.created, reverse=True)
    if not current_user or current_user.id != user.id:
        mods_created = [mod for mod in mods_created if mod.published]
    mods_followed = sorted(user.following, key=lambda mod: mod.created, reverse=True)
    return render_template("view_profile.html", profile=user, mods_created=mods_created, mods_followed=mods_followed)

@profiles.route("/profile/<username>/edit", methods=['GET', 'POST'])
@loginrequired
@with_session
def profile(username):
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
        profile.twitterUsername = request.form.get('twitter-username')
        profile.youtubeUsername = request.form.get('youtube-username')
        profile.twitchUsername = request.form.get('twitch-username')
        profile.facebookUsername = request.form.get('facebook-username')
        profile.forumUsername = request.form.get('forum-username')
        profile.showForumName = request.form.get('showForumName')
        profile.showIRCName = request.form.get('showIRCName')
        profile.showTwitterName = request.form.get('showTwitterName')
        profile.showRedditName = request.form.get('showRedditName')
        profile.showYoutubeName = request.form.get('showYoutubeName')
        profile.showTwitchName = request.form.get('showTwitchName')
        profile.showFacebookName = request.form.get('showFacebookName')
        # Due to the Forum update, and the fact that IPS4 doesn't have an API like 
        # vBullentin, we are removing this until we can adress it.
        # TODO(Thomas): Find a way to get the id of the User.
        # result = getForumId(profile.forumUsername)
        # if not result:
        #     profile.forumUsername = ''
        # else:
        #     profile.forumUsername = result['name']
        #     profile.forumId = result['id']
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
def make_public(username):
    if current_user.username != username:
        abort(401)
    current_user.public = True
    return redirect("/profile/" + current_user.username)
