from typing import Union
from flask import session
from flask.sessions import SecureCookieSessionInterface
from flask_login import current_user

class OnlyLoggedInSessionInterface(SecureCookieSessionInterface):

    """Don't send session cookies for anonymous users"""
    def save_session(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        # Check if current_user is None or not authenticated
        if not current_user or (hasattr(current_user, 'is_authenticated') and not current_user.is_authenticated):
            # Tell client to delete the session cookie
            session.clear()
        return super().save_session(*args, **kwargs)
