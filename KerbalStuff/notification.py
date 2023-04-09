import threading
import re
from flask import url_for
from typing import Dict, Iterable, Optional, Any
import requests

from .config import _cfg
from .objects import Mod, GameVersion, User, Notification, EnabledNotification
from .database import db

MAJOR_MINOR_PATCH_PATTERN = re.compile(r'^([^.]+\.[^.]+\.[^.]+)')


def send_add_notifications(mod: Mod) -> None:
    for enab_notif in mod.enabled_notifications:
        send_add_notification(enab_notif)


def send_add_notification(notif: EnabledNotification) -> None:
    if notif.notification.add_url and notif.mod.published:
        protocol = _cfg('protocol')
        domain = _cfg('domain')
        site_name = _cfg('site-name')
        authors = notif.mod.all_authors()
        if protocol and domain and site_name:
            storage = _cfg('storage')
            site_base_url = protocol + "://" + domain
            _bg_post(notif.notification.add_url,
                     {'name': notif.mod.name,
                      'id': notif.mod.id,
                      'license': notif.mod.license,
                      'username': [user.username for user in authors],
                      'user_github': [user.githubUsername for user in authors],
                      'user_forum_id': [user.forumId for user in authors],
                      'user_forum_username': [user.forumUsername for user in authors],
                      'email': [user.email for user in authors],
                      'user_url': [site_base_url + url_for("profile.view_profile",
                                                           username=user.username)
                                   for user in authors],
                      'short_description': notif.mod.short_description,
                      'description': notif.mod.description,
                      'external_link': notif.mod.external_link,
                      'source_link': notif.mod.source_link,
                      'mod_url': site_base_url + url_for('mods.mod',
                                                         mod_name=notif.mod.name,
                                                         mod_id=notif.mod.id),
                      'site_name': site_name,
                      'download_size': (notif.mod.default_version.format_size(storage)
                                        if notif.mod.default_version and storage else
                                        None)})


def send_change_notifications(mod: Mod, event_type: str, force: bool = False) -> None:
    for notif in mod.enabled_notifications:
        send_change_notification(notif, event_type, force)


def send_change_notification(notif: EnabledNotification, event_type: str, force: bool = False) -> None:
    if notif.notification.change_url and (notif.mod.published or force):
        _bg_post(notif.notification.change_url,
                 {'mod_id': notif.mod.id,
                  'event_type': event_type})


def _bg_post(url: str, data: Dict[str, Any]) -> None:
    """Fire and forget some data to a POST URL in a background thread"""
    threading.Thread(target=requests.post, args=(url, data)).start()


def import_game_versions(notif: Notification) -> None:
    if notif.builds_url:
        current_versions = {gv.friendly_version
                            for gv in notif.game.versions}
        for version in game_versions_from_notif(notif.builds_url,
                                                notif.builds_url_format,
                                                notif.builds_url_argument):
            if version not in current_versions:
                current_versions.add(version)
                db.add(GameVersion(friendly_version=version, game_id=notif.game_id))
                db.commit()


def game_versions_from_notif(url: str, fmt: str, argument: str) -> Iterable[str]:
    resp = requests.get(url)
    if fmt == 'plain_current':
        yield resp.text
    elif fmt == 'json_list':
        yield from resp.json()
    elif fmt == 'json_nested_dict_values':
        for _, full_version in resp.json()[argument].items():
            m = MAJOR_MINOR_PATCH_PATTERN.match(full_version)
            if m:
                yield m.groups()[0]
    else:
        raise Exception(f"Invalid builds format '{fmt}'")
