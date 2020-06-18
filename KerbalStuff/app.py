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
from typing import Tuple, List, Dict, Any, Optional, Union

import requests
from flask import Flask, render_template, g, url_for, Response, request
from flask_login import LoginManager, current_user
from flaskext.markdown import Markdown
from werkzeug.exceptions import HTTPException

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
from .config import _cfg, _cfgb, _cfgd, _cfgi
from .custom_json import CustomJSONEncoder
from .database import db
from .helpers import is_admin, following_mod, following_user
from .kerbdown import KerbDown
from .objects import User

app = Flask(__name__, template_folder='../templates')
app.jinja_env.filters['firstparagraph'] = firstparagraph
app.jinja_env.filters['remainingparagraphs'] = remainingparagraphs
app.secret_key = _cfg("secret-key")
app.jinja_env.cache = None
app.json_encoder = CustomJSONEncoder
markdown = Markdown(app, safe_mode='remove', extensions=[KerbDown()])
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(username: str) -> User:
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
    # Flask *first* checks if there is an error handler registered for a certain exception or status code,
    # *then* converts it to a 500 if it couldn't find any. So we can't just listen for 500s, they aren't 500s yet.
    # https://flask.palletsprojects.com/en/1.1.x/errorhandling/#unhandled-exceptions
    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception) -> Any:
        # shit
        try:
            db.rollback()
            db.close()
        except:
            # shit shit
            sys.exit(1)
        path = request.path
        if path.startswith('/api/'):
            return handle_api_exception(e)
        return render_template("internal_error.html"), 500

    # Error handler
    error_to = _cfg("error-to")
    if error_to:
        import logging
        from logging.handlers import SMTPHandler

        smtp_host = _cfg('smtp-host')
        smtp_port = _cfgi('smtp-port')
        error_from = _cfg('error-from')
        site_name = _cfg('site-name')
        if smtp_host and smtp_port and error_from and site_name:
            mail_handler = SMTPHandler((smtp_host, smtp_port),
                                       error_from, [error_to],
                                       site_name + ' Application Exception')
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


@app.errorhandler(404)
def handle_404(e: Exception) -> Any:
    path = request.path
    if path.startswith('/api/'):
        return handle_api_exception(e)
    return render_template("not_found.html"), 404


def handle_api_exception(e: Exception) -> Response:
    if isinstance(e, HTTPException):
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "error": True,
            "reason": f'{e.code} {e.name}: {e.description}',
            "code": e.code,
        })
    else:
        response = Response(json.dumps({
            "error": True,
            "reason": f'500 Internal Server Error: {str(e)}',
            "code": 500,
        }), 500)
    return response


# I am unsure if this function is still needed or rather, if it still works.
# TODO(Thomas): Investigate and remove
@app.route('/ksp-profile-proxy/<fragment>')
@json_output
def profile_proxy(fragment: str) -> List[Dict[str, Any]]:
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
def version() -> Response:
    return Response(subprocess.check_output(["git", "log", "-1"]), mimetype="text/plain")


@app.route('/hook', methods=['POST'])
def hook_publish() -> Union[str, Tuple[str, int]]:
    try:
        # Configuration sanity check
        hook_branch = _cfg("hook_branch")
        if not hook_branch:
            app.logger.info("No hook_branch is configured.")
            return "ignored"
        restart_command = _cfg("restart_command")
        if not restart_command:
            app.logger.info("No restart_command is configured.")
            return "ignored"
        # Make sure it's from GitHub
        if not sig_match(request.headers.get("X-Hub-Signature", ''), request.data):
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
        app.logger.info("Received push event from github. Starting update process...")
        update_from_github.delay(os.getcwd(), hook_branch, restart_command)
        return "thanks"
    except Exception:
        app.logger.exception('Unable to process github hook data')
        return "internal server error", 500


def sig_match(req_sig: Optional[str], body: bytes) -> bool:
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
def find_dnt() -> None:
    field = "Dnt"
    do_not_track = False
    if field in request.headers:
        do_not_track = True if request.headers[field] == "1" else False
    g.do_not_track = do_not_track


@app.context_processor
def inject() -> Dict[str, Any]:
    protocol = _cfg('protocol')
    domain = _cfg('domain')
    if not protocol or not domain:
        return dict()
    first_visit = True
    dismissed_donation = False
    if request.cookies.get('first_visit') is not None:
        first_visit = False
    if request.cookies.get('dismissed_donation') is not None:
        dismissed_donation = True
    return {
        'mobile': False,
        'ua_platform': getattr(request.user_agent, 'platform', None),
        'analytics_id': _cfg("google_analytics_id"),
        'analytics_domain': _cfg("google_analytics_domain"),
        'disqus_id': _cfg("disqus_id"),
        'dnt': True,
        'ads': False,
        'ad_id': _cfg("project_wonderful_id"),
        'root': protocol + "://" + domain,
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
        'support_channels': _cfgd('support-channels'),
        'donation_link': _cfg('donation-link'),
        'donation_header_link': _cfgb('donation-header-link') if not dismissed_donation else False,
        'registration': _cfgb('registration')
    }
