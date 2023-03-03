import html
from typing import Iterable, Optional

from flask import url_for
from jinja2 import Template
from werkzeug.utils import secure_filename

from flask import render_template

from .objects import User, Mod, ModVersion, Following
from .celery import send_mail
from .config import _cfg, _cfgd


def send_confirmation(user: User, followMod: Optional[str] = None) -> None:
    site_name = _cfg('site-name')
    if site_name:
        with open("emails/confirm-account") as f:
            if followMod is not None:
                message = Template(f.read()).render({'user': user, 'site_name': site_name, "domain": _cfg("domain"),
                                                    'confirmation': user.confirmation + "?f=" + followMod})
            else:
                message = html.unescape(
                    Template(f.read()).render({'user': user, 'site_name': site_name, "domain": _cfg("domain"),
                                              'confirmation': user.confirmation}))
        send_mail.delay(_cfg('support-mail'), [user.email], "Welcome to " + site_name + "!", message,
                        important=True)


def send_password_reset(user: User) -> None:
    site_name = _cfg('site-name')
    if site_name:
        with open("emails/password-reset") as f:
            message = html.unescape(
                Template(f.read()).render({'user': user, 'site_name': site_name, "domain": _cfg("domain"),
                                          'confirmation': user.passwordReset}))
        send_mail.delay(_cfg('support-mail'), [user.email], "Reset your password on " + site_name, message,
                        important=True)


def send_password_changed(user: User) -> None:
    with open("emails/password-changed") as f:
        message = html.unescape(
            Template(f.read()).render({
                'user': user,
                'site_name': _cfg('site-name'),
                "domain": _cfg("domain"),
                'support_channels': _cfgd('support-channels')
            })
        )
    send_mail.delay(_cfg('support-mail'), [user.email], f'Your password on {_cfg("site-name")} has been changed',
                    message, important=True)


def send_mod_locked(mod: Mod, user: User) -> None:
    support_channels = list()
    for name, url in _cfgd('support-channels').items():
        support_channels.append({'name': name, 'channel_url': url})

    with open('emails/mod-locked') as f:
        message = html.unescape(
            Template(f.read()).render({
                'mod': mod, 'user': user,
                'url': url_for('mods.mod', mod_id=mod.id, mod_name=mod.name, _external=True),
                'site_name': _cfg('site-name'),
                'support_channels': _cfgd('support-channels')
            })
        )
        subject = f'Your mod {mod.name} has been locked on {_cfg("site-name")}'
    send_mail.delay(_cfg('support-mail'), [user.email], subject, message, important=True)


def send_grant_notice(mod: Mod, user: User) -> None:
    site_name = _cfg('site-name')
    if site_name:
        with open("emails/grant-notice") as f:
            message = html.unescape(
                Template(f.read()).render({'user': user, 'site_name': site_name, "domain": _cfg("domain"),
                                          'mod': mod, 'url': url_for('mods.mod', mod_id=mod.id, mod_name=mod.name)}))
        send_mail.delay(_cfg('support-mail'), [user.email], "You've been asked to co-author a mod on " + site_name,
                        message, important=True)


def send_update_notification(mod: Mod, version: ModVersion, user: User) -> None:
    followers = (fol.user.email for fol
                 in Following.query.filter(Following.mod_id == mod.id,
                                           Following.send_update == True))
    changelog = version.changelog
    if changelog:
        changelog = '\n'.join(['    ' + line for line in changelog.split('\n')])

    targets = list()
    for follower in followers:
        targets.append(follower)
    if len(targets) == 0:
        return
    with open("emails/mod-updated") as f:
        message = html.unescape(Template(f.read()).render({
            'mod': mod,
            'user': user,
            'site_name': _cfg('site-name'),
            'domain': _cfg("domain"),
            'latest': version,
            'url': '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64],
            'changelog': changelog
        }))
    html_message = render_template(
        "email-mod-updated.html",
        mod=mod,
        user=user,
        site_name=_cfg('site-name'),
        domain=_cfg('domain'),
        latest=version,
        url=f'/mod/{mod.id}/{secure_filename(mod.name)[:64]}',
        changelog=version.changelog)
    subject = f'{user.username} has just updated {mod.name}!'
    send_mail.delay(_cfg('support-mail'), targets, subject, message, html_message=html_message)


def send_autoupdate_notification(mod: Mod) -> None:
    followers = (fol.user.email for fol
                 in Following.query.filter(Following.mod_id == mod.id,
                                           Following.send_autoupdate == True))
    targets = list()
    for follower in followers:
        targets.append(follower)
    if len(targets) == 0:
        return
    with open("emails/mod-autoupdated") as f:
        message = html.unescape(Template(f.read()).render({
            'mod': mod,
            'domain': _cfg("domain"),
            'latest': mod.default_version,
            'url': '/mod/' + str(mod.id) + '/' + secure_filename(mod.name)[:64]
        }))
    html_message = render_template(
        "email-mod-autoupdated.html",
        mod=mod,
        domain=_cfg('domain'),
        latest=mod.default_version,
        url=f'/mod/{mod.id}/{secure_filename(mod.name)[:64]}')
    subject = f'{mod.name} is compatible with {mod.game.name} {mod.default_version.gameversion.friendly_version}!'
    send_mail.delay(_cfg('support-mail'), targets, subject, message, html_message=html_message)


def send_bulk_email(users: Iterable[User], subject: str, body: str) -> None:
    targets = list()
    for u in users:
        targets.append(u)
    send_mail.delay(_cfg('support-mail'), targets, subject, body)
