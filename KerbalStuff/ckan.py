import threading
import requests
import re
from flask import url_for
from typing import Dict, Iterable, Optional, Any

from .config import _cfg
from .objects import Mod, Game, GameVersion, User
from .database import db

CKAN_KSP_BUILDS_URL  = 'https://github.com/KSP-CKAN/CKAN-meta/raw/master/builds.json'
CKAN_KSP2_BUILDS_URL = 'https://github.com/KSP-CKAN/KSP2-CKAN-meta/raw/main/builds.json'
MAJOR_MINOR_PATCH_PATTERN = re.compile(r'^([^.]+\.[^.]+\.[^.]+)')


def send_to_ckan(mod: Mod) -> None:
    protocol = _cfg('protocol')
    domain = _cfg('domain')
    url = _cfg('create-url')
    site_name = _cfg('site-name')
    storage = _cfg('storage')
    if mod.ckan and mod.published and url and protocol and domain and site_name:
        site_base_url = protocol + "://" + domain
        _bg_post(url, {
            'name': mod.name,
            'id': mod.id,
            'license': mod.license,
            **user_fields(mod.user),
            'shared_authors': [user_fields(sh.user)
                               for sh in mod.shared_authors
                               if sh.accepted],
            'short_description': mod.short_description,
            'description': mod.description,
            'external_link': mod.external_link,
            'source_link': mod.source_link,
            'user_url': site_base_url + url_for("profile.view_profile", username=mod.user.username),
            'mod_url': site_base_url + url_for('mods.mod', mod_name=mod.name, mod_id=mod.id),
            'site_name': site_name,
            'download_size': (mod.default_version.format_size(storage)
                              if mod.default_version and storage else
                              None),
        })


def user_fields(user: User) -> Dict[str, str]:
    return {'username': user.username,
            'user_github': user.githubUsername,
            'user_forum_id': user.forumId,
            'user_forum_username': user.forumUsername,
            'email': user.email}


def notify_ckan(mod: Mod, event_type: str, force: bool = False) -> None:
    url = _cfg("notify-url")
    if mod.ckan and url and (mod.published or force):
        _bg_post(url, {
            'mod_id': mod.id,
            'event_type': event_type,
        })


def _bg_post(url: str, data: Dict[str, Any]) -> None:
    """Fire and forget some data to a POST URL in a background thread"""
    threading.Thread(target=requests.post, args=(url, data)).start()


def import_ksp_versions_from_ckan(ksp_game_id: int) -> None:
    _import_game_versions(ksp_game_id, ksp_versions_from_ckan())


def import_ksp2_versions_from_ckan(ksp2_game_id: int) -> None:
    _import_game_versions(ksp2_game_id, ksp2_versions_from_ckan())


def ksp_versions_from_ckan() -> Iterable[str]:
    builds = requests.get(CKAN_KSP_BUILDS_URL).json()
    for _, full_version in builds['builds'].items():
        m = MAJOR_MINOR_PATCH_PATTERN.match(full_version)
        if m:
            yield m.groups()[0]


def ksp2_versions_from_ckan() -> Iterable[str]:
    return requests.get(CKAN_KSP2_BUILDS_URL).json()


def _import_game_versions(game_id: int, new_versions: Iterable[str]) -> None:
    current_versions = {gv.friendly_version
                        for gv in Game.query.get(game_id).versions}
    for version in new_versions:
        if version not in current_versions:
            current_versions.add(version)
            db.add(GameVersion(friendly_version=version, game_id=game_id))
            db.commit()
