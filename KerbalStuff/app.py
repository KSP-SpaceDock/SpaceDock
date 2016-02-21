from flask import Flask, render_template, request, g, Response, redirect, session, abort, send_file, url_for
from flask.ext.login import LoginManager, current_user
from flaskext.markdown import Markdown
from jinja2 import FileSystemLoader, ChoiceLoader
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from shutil import rmtree, copyfile
from sqlalchemy import desc
from time import strftime

import sys
import os
import subprocess
import urllib
import requests
import json
import zipfile
import locale
import traceback
import xml.etree.ElementTree as ET

from KerbalStuff.config import _cfg, _cfgi, _cfgb
from KerbalStuff.database import db, init_db
from KerbalStuff.helpers import *
from KerbalStuff.common import *
from KerbalStuff.network import *
from KerbalStuff.custom_json import CustomJSONEncoder
from KerbalStuff.kerbdown import KerbDown
from KerbalStuff.objects import User

from KerbalStuff.blueprints.login_oauth import list_defined_oauths
from KerbalStuff.blueprints.profile import profiles
from KerbalStuff.blueprints.accounts import accounts
from KerbalStuff.blueprints.login_oauth import login_oauth
from KerbalStuff.blueprints.anonymous import anonymous
from KerbalStuff.blueprints.blog import blog
from KerbalStuff.blueprints.admin import admin
from KerbalStuff.blueprints.mods import mods
from KerbalStuff.blueprints.lists import lists
from KerbalStuff.blueprints.api import api

app = Flask(__name__)
app.jinja_env.filters['firstparagraph'] = firstparagraph
app.jinja_env.filters['remainingparagraphs'] = remainingparagraphs
app.secret_key = _cfg("secret-key")
app.jinja_env.cache = None
app.json_encoder = CustomJSONEncoder
markdown = Markdown(app, safe_mode='remove', extensions=[KerbDown()])
init_db()
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
        pass # give up

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
    if _cfg("error-to") != "":
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler((_cfg("smtp-host"), _cfg("smtp-port")),
           _cfg("error-from"),
           [_cfg("error-to")],
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
    r = requests.post("http://forum.kerbalspaceprogram.com/ajax.php?do=usersearch", data= {
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
    allow = False
    for ip in _cfg("hook_ips").split(","):
        parts = ip.split("/")
        range = 32
        if len(parts) != 1:
            range = int(parts[1])
        addr = networkMask(parts[0], range)
        if addressInNetwork(dottedQuadToNum(request.remote_addr), addr):
            allow = True
    if not allow:
        return "unauthorized", 403
    # Pull and restart site
    event = json.loads(request.data.decode("utf-8"))
    if not _cfg("hook_repository") == "%s/%s" % (event["repository"]["owner"]["name"], event["repository"]["name"]):
        return "ignored"
    if any("[noupdate]" in c["message"] for c in event["commits"]):
        return "ignored"
    if "refs/heads/" + _cfg("hook_branch") == event["ref"]:
        subprocess.call(["git", "pull", "origin", "master"])
        subprocess.Popen(_cfg("restart_command").split())
        return "thanks"
    return "ignored"

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
    ads = True
    first_visit = True
    dismissed_donation = False
    if 'ad-opt-out' in request.cookies:
        ads = False
    if g.do_not_track:
        ads = False
    if not _cfg("project_wonderful_id"):
        ads = False
    if request.cookies.get('first_visit') != None:
        first_visit = False
    if request.cookies.get('dismissed_donation') != None:
        dismissed_donation = True
    return {
        'mobile': g.mobile,
        'ua_platform': request.user_agent.platform,
        'analytics_id': _cfg("google_analytics_id"),
        'analytics_domain': _cfg("google_analytics_domain"),
        'disqus_id': _cfg("disqus_id"),
        'dnt': g.do_not_track,
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
        'donation_header_link': _cfgb('donation-header-link') if not dismissed_donation else False
    }
