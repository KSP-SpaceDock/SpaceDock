import os
from pathlib import Path
from shutil import move
from typing import Optional

import pyclamd

from .config import _cfg, _cfgi, site_logger
from .objects import User
from .email import send_mod_locked
from .ckan import notify_ckan

clam_daemon = None


def file_contains_malware(where: str) -> bool:
    global clam_daemon
    try:
        if not clam_daemon:
            clam_daemon = pyclamd.ClamdNetworkSocket(host=_cfg('clamav-host'), port=_cfgi('clamav-port', 3310))
        result = clam_daemon.scan_file(where)
        if result:
            site_logger.error(f'ClamAV says {where} contains malware')
            return True
    except Exception as exc:
        # No ClamAV daemon found, log it and let the file through
        site_logger.error(f'Failed to connect to ClamAV, skipping scan of {where}', exc_info=exc)
    return False


def quarantine_malware(path: str) -> None:
    quarantine_folder = _cfg('clamav-quarantine-path')
    if quarantine_folder:
        move(path, Path(quarantine_folder) / Path(path).name)
    else:
        os.remove(path)


def punish_malware(user: User) -> None:
    # Lock all of this author's mods
    for other_mod in user.mods:
        if not other_mod.locked:
            other_mod.locked = True
            other_mod.published = False
            other_mod.locked_by = None
            other_mod.lock_reason = 'Malware detected in upload'
            send_mod_locked(other_mod, user)
            notify_ckan(other_mod, 'locked', True)
