from flask_login import current_user
from .objects import Mod


def is_admin() -> bool:
    if not current_user:
        return False
    return current_user.admin


def following_mod(mod: Mod) -> bool:
    if not current_user:
        return False
    if any(m.id == mod.id for m in current_user.following):
        return True
    return False
