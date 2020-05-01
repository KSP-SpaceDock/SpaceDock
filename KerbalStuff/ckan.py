import threading
import requests
from flask import url_for

from .config import _cfg


def send_to_ckan(mod):
    if mod.ckan and _cfg("create-url"):
        site_base_url = _cfg("protocol") + "://" + _cfg("domain")
        _bg_post(_cfg("create-url"), {
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
            'site_name': _cfg('site-name'),
        })


def notify_ckan(mod, event_type):
    if mod.ckan and _cfg("notify-url"):
        _bg_post(_cfg("notify-url"), {
            'mod_id': mod.id,
            'event_type': event_type,
        })


def _bg_post(url, data):
    """Fire and forget some data to a POST URL in a background thread"""
    threading.Thread(target=requests.post, args=(url, data)).start()
