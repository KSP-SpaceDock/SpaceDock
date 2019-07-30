from flask_login import current_user


def is_admin():
    if not current_user:
        return False
    return current_user.admin


def following_mod(mod):
    if not current_user:
        return False
    if any(m.id == mod.id for m in current_user.following):
        return True
    return False


def following_user(mod):
    return False
