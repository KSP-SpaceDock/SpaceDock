import threading
import requests
from flask import url_for
from typing import Dict

from .config import _cfg
from .objects import Mod


def send_to_ckan(mod: Mod) -> None:
    protocol = _cfg('protocol')
    domain = _cfg('domain')
    url = _cfg('create-url')
    site_name = _cfg('site-name')
    if mod.ckan and mod.published and url and protocol and domain and site_name:
        site_base_url = protocol + "://" + domain
        _bg_post(url, {
            'name': mod.name,
            'id': mod.id,
            'license': mod.license,
            'username': mod.user.username,
            'email': mod.user.email,
            'short_description': mod.short_description,
            'description': mod.description,
            'external_link': mod.external_link,
            'user_url': site_base_url + url_for("profile.view_profile", username=mod.user.username),
            'mod_url': site_base_url + url_for('mods.mod', mod_name=mod.name, mod_id=mod.id),
            'site_name': site_name,
        })


def notify_ckan(mod: Mod, event_type: str) -> None:
    url = _cfg("notify-url")
    if mod.ckan and mod.published and url:
        _bg_post(url, {
            'mod_id': mod.id,
            'event_type': event_type,
        })


def _bg_post(url: str, data: Dict[str, str]) -> None:
    """Fire and forget some data to a POST URL in a background thread"""
    threading.Thread(target=requests.post, args=(url, data)).start()
