import smtplib
import pystache
import os
import html.parser
import threading
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
from flask import url_for

from SpaceDock.database import db
from SpaceDock.objects import User
from SpaceDock.config import _cfg, _cfgi
from SpaceDock.celery import send_mail

def send_confirmation(user, followMod=None):
    with open("emails/confirm-account") as f:
        if followMod != None:
            message = pystache.render(f.read(), { 'user': user, 'site-name': _cfg('site-name'), "domain": _cfg("domain"),\
                    'confirmation': user.confirmation + "?f=" + followMod })
        else:
            message = html.parser.HTMLParser().unescape(\
                    pystache.render(f.read(), { 'user': user, 'site-name': _cfg('site-name'), "domain": _cfg("domain"), 'confirmation': user.confirmation }))
    send_mail.delay(_cfg('support-mail'), [ user.email ], "Welcome to " + _cfg('site-name') + "!", message, important=True)

def send_reset(user):
    with open("emails/password-reset") as f:
        message = html.parser.HTMLParser().unescape(\
                pystache.render(f.read(), { 'user': user, 'site-name': _cfg('site-name'), "domain": _cfg("domain"), 'confirmation': user.passwordReset }))
    send_mail.delay(_cfg('support-mail'), [ user.email ], "Reset your password on " + _cfg('site-name'), message, important=True)

def send_grant_notice(mod, user):
    with open("emails/grant-notice") as f:
        message = html.parser.HTMLParser().unescape(\
                pystache.render(f.read(), { 'user': user, 'site-name': _cfg('site-name'), "domain": _cfg("domain"),\
                'mod': mod, 'url': url_for('mods.mod', id=mod.id, mod_name=mod.name) }))
    send_mail.delay(_cfg('support-mail'), [ user.email ], "You've been asked to co-author a mod on " + _cfg('site-name'), message, important=True)

def send_update_notification(mod, version, user):
    followers = [u.email for u in mod.followers]
    changelog = version.changelog
    if changelog:
        changelog = '\n'.join(['    ' + l for l in changelog.split('\n')])

    targets = list()
    for follower in followers:
        targets.append(follower)
    if len(targets) == 0:
        return
    with open("emails/mod-updated") as f:
        message = html.parser.HTMLParser().unescape(pystache.render(f.read(),
            {
                'mod': mod,
                'user': user,
                'site-name': _cfg('site-name'),
                'domain': _cfg("domain"),
                'latest': version,
                'url': '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64],
                'changelog': changelog
            }))
    subject = user.username + " has just updated " + mod.name + "!"
    send_mail.delay(_cfg('support-mail'), targets, subject, message)

def send_autoupdate_notification(mod):
    followers = [u.email for u in mod.followers]
    changelog = mod.default_version().changelog
    if changelog:
        changelog = '\n'.join(['    ' + l for l in changelog.split('\n')])

    targets = list()
    for follower in followers:
        targets.append(follower)
    if len(targets) == 0:
        return
    with open("emails/mod-autoupdated") as f:
        message = html.parser.HTMLParser().unescape(pystache.render(f.read(),
            {
                'mod': mod,
                'domain': _cfg("domain"),
                'site-name': _cfg('site-name'),
                'latest': mod.default_version(),
                'url': '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64],
                'changelog': changelog
            }))
	# We (or rather just me) probably want that this is not dependent on KSP, since I know some people
	# who run forks of SpaceDock for non-KSP purposes.
	# TODO(Thomas): Consider in putting the game name into a config.
    subject = mod.name + " is compatible with Game " + mod.versions[0].gameversion.friendly_version + "!"
    send_mail.delay(_cfg('support-mail'), targets, subject, message)

def send_bulk_email(users, subject, body):
    targets = list()
    for u in users:
        targets.append(u)
    send_mail.delay(_cfg('support-mail'), targets, subject, body)
