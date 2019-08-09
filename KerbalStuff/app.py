import hashlib
import hmac
import json
import locale
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from time import strftime

import requests
from flask import Flask, render_template, g, url_for, Response, request
from flask_login import LoginManager, current_user
from flaskext.markdown import Markdown
from jinja2 import FileSystemLoader, ChoiceLoader

from .blueprints.accounts import accounts
from .blueprints.admin import admin
from .blueprints.anonymous import anonymous
from .blueprints.api import api
from .blueprints.blog import blog
from .blueprints.lists import lists
from .blueprints.login_oauth import list_defined_oauths, login_oauth
from .blueprints.mods import mods
from .blueprints.profile import profiles
from .celery import update_from_github
from .common import firstparagraph, remainingparagraphs, json_output, wrap_mod, dumb_object
from .config import _cfg, _cfgb
from .custom_json import CustomJSONEncoder
from .database import db
from .helpers import is_admin, following_mod, following_user
from .kerbdown import KerbDown
from .objects import User

app = Flask(__name__)
app.jinja_env.filters['firstparagraph'] = firstparagraph
app.jinja_env.filters['remainingparagraphs'] = remainingparagraphs
app.secret_key = _cfg("secret-key")
app.jinja_env.cache = None
app.json_encoder = CustomJSONEncoder
markdown = Markdown(app, safe_mode='remove', extensions=[KerbDown()])
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(username):
    return User.query.filter(User.username == username).first()


login_manager.anonymous_user = lambda: None

app.register_blueprint(profiles)
app.register_blueprint(accounts)
app.register_blueprint(login_oauth)
app.register_blueprint(anonymous)
app.register_blueprint(blog)
app.register_blueprint(admin)
app.register_blueprint(mods)
app.register_blueprint(lists)
app.register_blueprint(api)

try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en')
    except:
        pass  # give up

if not app.debug:
    @app.errorhandler(500)
    def handle_500(e):
        # shit
        try:
            db.rollback()
            db.close()
        except:
            # shit shit
            sys.exit(1)
        return render_template("internal_error.html"), 500


    # Error handler
    error_to = _cfg("error-to")
    if error_to:
        import logging
        from logging.handlers import SMTPHandler

        mail_handler = SMTPHandler((_cfg("smtp-host"), _cfg("smtp-port")),
                                   _cfg("error-from"), [error_to],
                                   _cfg('site-name') + ' Application Exception')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


@app.errorhandler(404)
def handle_404(e):
    return render_template("not_found.html"), 404


# I am unsure if this function is still needed or rather, if it still works.
# TODO(Thomas): Investigate and remove
@app.route('/ksp-profile-proxy/<fragment>')
@json_output
def profile_proxy(fragment):
    r = requests.post("http://forum.kerbalspaceprogram.com/ajax.php?do=usersearch",
                      data={
                          'securitytoken': 'guest',
                          'do': 'usersearch',
                          'fragment': fragment
                      })
    root = ET.fromstring(r.text)
    results = list()
    for child in root:
        results.append({
            'id': child.attrib['userid'],
            'name': child.text
        })
    return results


@app.route('/version')
def version():
    return Response(subprocess.check_output(["git", "log", "-1"]), mimetype="text/plain")


@app.route('/hook', methods=['POST'])
def hook_publish():
    try:
        # Make sure it's from GitHub
        if not sig_match(request.headers.get("X-Hub-Signature"), request.data):
            app.logger.warning("X-Hub-Signature didn't match the request data")
            return "unauthorized", 403
        event = json.loads(request.data.decode("utf-8"))
        # Make sure it's the right repo
        expected_repo = _cfg("hook_repository")
        repo_id = event["repository"]["full_name"]
        if not expected_repo == repo_id:
            app.logger.info("Wrong repository. Expected '%s', got '%s'", expected_repo, repo_id)
            return "ignored"
        # Make sure it's the right branch
        hook_branch = _cfg("hook_branch")
        expected_ref = "refs/heads/" + hook_branch
        ref_id = event["ref"]
        if expected_ref != ref_id:
            app.logger.info("Wrong branch. Expected '%s', got '%s'", expected_ref, ref_id)
            return "ignored"
        # Skip if we put "[noupdate]" in any of the commit messages
        if any("[noupdate]" in c["message"] for c in event["commits"]):
            app.logger.info("A commit in the update is tagged [noupdate]. Ignoring the update.")
            return "ignored"
        # Pull and restart site
        update_from_github.delay(os.getcwd(), hook_branch)
        return "thanks"
    except Exception:
        app.logger.exception('Unable to process github hook data')
        return "internal server error", 500


def sig_match(req_sig, body):
    # Make sure a secret is defined in our config
    hook_secret = _cfg("hook_secret")
    if not hook_secret:
        app.logger.warning('No hook_secret is configured')
        return False
    # Make sure a sig was sent
    if req_sig is None:
        app.logger.warning('No signature provided in the request')
        return False
    # Make sure they match
    # compare_digest takes the same time regardless of how similar the strings are
    # (to make it harder for hackers)
    secret_sig = "sha1=" + hmac.new(hook_secret.encode('ascii'), body, hashlib.sha1).hexdigest()
    return hmac.compare_digest(req_sig, secret_sig)


@app.before_request
def find_dnt():
    field = "Dnt"
    do_not_track = False
    if field in request.headers:
        do_not_track = True if request.headers[field] == "1" else False
    g.do_not_track = do_not_track


@app.before_request
def jinja_template_loader():
    mobile = request.user_agent.platform in ['android', 'iphone', 'ipad'] \
             or 'windows phone' in request.user_agent.string.lower() \
             or 'mobile' in request.user_agent.string.lower()
    g.mobile = mobile
    if mobile:
        app.jinja_loader = ChoiceLoader([
            FileSystemLoader(os.path.join("templates", "mobile")),
            FileSystemLoader("templates"),
        ])
    else:
        app.jinja_loader = FileSystemLoader("templates")


@app.context_processor
def inject():
    ads = False
    first_visit = True
    dismissed_donation = False
    if 'ad-opt-out' in request.cookies:
        ads = False
    # if g.do_not_track:
    #     ads = False
    if not _cfg("project_wonderful_id"):
        ads = False
    if request.cookies.get('first_visit') is not None:
        first_visit = False
    if request.cookies.get('dismissed_donation') is not None:
        dismissed_donation = True
    # 'mobile': g.mobile,
    # 'dnt': g.do_not_track,
    return {
        'mobile': False,
        'ua_platform': request.user_agent.platform,
        'analytics_id': _cfg("google_analytics_id"),
        'analytics_domain': _cfg("google_analytics_domain"),
        'disqus_id': _cfg("disqus_id"),
        'dnt': True,
        'ads': ads,
        'ad_id': _cfg("project_wonderful_id"),
        'root': _cfg("protocol") + "://" + _cfg("domain"),
        'domain': _cfg("domain"),
        'user': current_user,
        'len': len,
        'any': any,
        'following_mod': following_mod,
        'following_user': following_user,
        'admin': is_admin(),
        'oauth_providers': list_defined_oauths(),
        'wrap_mod': wrap_mod,
        'dumb_object': dumb_object,
        'first_visit': first_visit,
        'request': request,
        'locale': locale,
        'url_for': url_for,
        'strftime': strftime,
        'datetime': datetime,
        'site_name': _cfg('site-name'),
        'support_mail': _cfg('support-mail'),
        'source_code': _cfg('source-code'),
        'irc_channel': _cfg('irc-channel'),
        'donation_link': _cfg('donation-link'),
        'donation_header_link': _cfgb('donation-header-link') if not dismissed_donation else False,
        'registration': _cfgb('registration')
    }
