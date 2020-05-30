import html
from typing import Iterable

import chevron
from flask import url_for
from werkzeug.utils import secure_filename

from .objects import User, Mod, ModVersion
from .celery import send_mail
from .config import _cfg, _cfgd


def send_confirmation(user: User, followMod: str = None) -> None:
    site_name = _cfg('site-name')
    if site_name:
        with open("emails/confirm-account") as f:
            if followMod is not None:
                message = chevron.render(f.read(), {'user': user, 'site-name': site_name, "domain": _cfg("domain"),
                                                    'confirmation': user.confirmation + "?f=" + followMod})
            else:
                message = html.unescape(
                    chevron.render(f.read(), {'user': user, 'site-name': site_name, "domain": _cfg("domain"),
                                              'confirmation': user.confirmation}))
        send_mail.delay(_cfg('support-mail'), [user.email], "Welcome to " + site_name + "!", message,
                        important=True)


def send_reset(user: User) -> None:
    site_name = _cfg('site-name')
    if site_name:
        with open("emails/password-reset") as f:
            message = html.unescape(
                chevron.render(f.read(), {'user': user, 'site-name': site_name, "domain": _cfg("domain"),
                                          'confirmation': user.passwordReset}))
        send_mail.delay(_cfg('support-mail'), [user.email], "Reset your password on " + site_name, message,
                        important=True)


def send_mod_locked(mod: Mod, user: User) -> None:
    support_channels = list()
    for name, url in _cfgd('support-channels').items():
        support_channels.append({'name': name, 'channel_url': url})

    with open('emails/mod-locked') as f:
        message = html.unescape(
            chevron.render(f.read(), {
                'mod': mod, 'user': user,
                'url': url_for('mods.mod', mod_id=mod.id, mod_name=mod.name, _external=True),
                'site_name': _cfg('site-name'),
                'support_channels': support_channels
            })
        )
        subject = f'Your mod {mod.name} has been locked on {_cfg("site-name")}'
    send_mail.delay(_cfg('support-mail'), [user.email], subject, message, important=True)


def send_grant_notice(mod: Mod, user: User) -> None:
    site_name = _cfg('site-name')
    if site_name:
        with open("emails/grant-notice") as f:
            message = html.unescape(
                chevron.render(f.read(), {'user': user, 'site-name': site_name, "domain": _cfg("domain"),
                                          'mod': mod, 'url': url_for('mods.mod', mod_id=mod.id, mod_name=mod.name)}))
        send_mail.delay(_cfg('support-mail'), [user.email], "You've been asked to co-author a mod on " + site_name,
                        message, important=True)


def send_update_notification(mod: Mod, version: ModVersion, user: User) -> None:
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
        message = html.unescape(chevron.render(f.read(), {
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


def send_autoupdate_notification(mod: Mod) -> None:
    followers = [u.email for u in mod.followers]
    changelog = mod.default_version.changelog
    if changelog:
        changelog = '\n'.join(['    ' + l for l in changelog.split('\n')])

    targets = list()
    for follower in followers:
        targets.append(follower)
    if len(targets) == 0:
        return
    with open("emails/mod-autoupdated") as f:
        message = html.unescape(chevron.render(f.read(), {
            'mod': mod,
            'domain': _cfg("domain"),
            'site-name': _cfg('site-name'),
            'latest': mod.default_version,
            'url': '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64],
            'changelog': changelog
        }))
    # We (or rather just me) probably want that this is not dependent on KSP, since I know some people
    # who run forks of KerbalStuff for non-KSP purposes.
    # TODO(Thomas): Consider in putting the game name into a config.
    subject = mod.name + " is compatible with Game " + \
        mod.versions[0].gameversion.friendly_version + "!"
    send_mail.delay(_cfg('support-mail'), targets, subject, message)


def send_bulk_email(users: Iterable[User], subject: str, body: str) -> None:
    targets = list()
    for u in users:
        targets.append(u)
    send_mail.delay(_cfg('support-mail'), targets, subject, body)
