import binascii
import os
from collections import OrderedDict
from typing import List, Dict, Optional, Union, Tuple, Any
import werkzeug.wrappers

from flask import Blueprint, render_template, request, redirect, session, jsonify, url_for, \
    current_app
from flask_login import current_user, login_user
from flask_oauthlib.client import OAuth, OAuthRemoteApp

from .accounts import check_username_for_registration, \
    check_email_for_registration
from ..config import _cfg
from ..database import db
from ..email import send_confirmation
from ..objects import User, UserAuth

login_oauth = Blueprint('login_oauth', __name__)


# Python doesn't like OrderedDict with brackets, but mypy is fine with it
DEFINED_OAUTHS: Optional['OrderedDict[str, Dict[str, Any]]'] = None


def list_connected_oauths(user: User) -> List[str]:
    return [a.provider for a in UserAuth.query.filter(UserAuth.user_id == user.id)]


def list_defined_oauths() -> 'OrderedDict[str, Dict[str, Any]]':
    global DEFINED_OAUTHS
    if DEFINED_OAUTHS is not None:
        return DEFINED_OAUTHS
    master_list = OrderedDict()
    master_list['github'] = {
        'full_name': 'GitHub',
        'icon': 'github',
    }
    master_list['google'] = {
        'full_name': 'Google',
        'icon': 'google',
    }
    master_list['facebook'] = {
        'full_name': 'Facebook',
        'icon': 'facebook-official',
    }
    for p in list(master_list.keys()):
        if not is_oauth_provider_configured(p):
            del master_list[p]
    DEFINED_OAUTHS = master_list
    return DEFINED_OAUTHS


def is_oauth_provider_configured(provider: str) -> bool:
    if provider == 'github':
        return bool(_cfg('gh-oauth-id')) and bool(_cfg('gh-oauth-secret'))
    if provider == 'google':
        return (bool(_cfg('google-oauth-id')) and
                bool(_cfg('google-oauth-secret')))
    return False


def get_github_oath() -> Tuple[str, OAuthRemoteApp]:
    github = get_oauth_provider('github')
    resp = github.authorized_response()
    if resp is None:
        raise Exception(
            f"Access denied: reason={request.args['error']} error={request.args['error_description']}")
    if 'error' in resp:
        return jsonify(resp)
    session['github_token'] = (resp['access_token'], '')
    gh_info = github.get('user').data
    return gh_info['login'], github


def _connect_with_oauth_finalize(remote_user: str, provider: str) -> Union[str, werkzeug.wrappers.Response]:
    if not current_user:
        return 'Trying to associate an account, but not logged in?'
    auth = UserAuth.query.filter(UserAuth.provider == provider,
                                 UserAuth.remote_user == remote_user).first()
    if auth:
        if auth.user_id == current_user.id:
            # You're already set up.
            return redirect('/profile/%s/edit' % current_user.username)
        # This account is already connected with some user.
        full_name = list_defined_oauths()[provider]['full_name']
        return 'Your %s account is already connected to a SpaceDock account.' % full_name
    auth = UserAuth(user_id=current_user.id,
                    remote_user=remote_user,
                    provider=provider)
    db.add(auth)
    db.flush()  # So that /profile will display currectly
    return redirect('/profile/%s/edit' % current_user.username)


@login_oauth.route("/login-oauth", methods=['GET', 'POST'])
def login_with_oauth() -> Union[str, werkzeug.wrappers.Response]:
    if request.method == 'GET':
        return redirect('/login')
    provider = request.form.get('provider', '')
    if not is_oauth_provider_configured(provider):
        return 'This install is not configured for login with %s' % provider
    oauth = get_oauth_provider(provider)
    callback = "{}://{}{}".format(_cfg("protocol"), _cfg("domain"),
                                  url_for('.login_with_oauth_authorized_' + provider))
    return oauth.authorize(callback=callback)


@login_oauth.route("/connect-oauth", methods=['POST'])
def connect_with_oauth() -> Union[str, werkzeug.wrappers.Response]:
    provider = request.form.get('provider', '')
    if not is_oauth_provider_configured(provider):
        return 'This install is not configured for login with %s' % provider
    oauth = get_oauth_provider(provider)
    callback = "{}://{}{}".format(_cfg("protocol"), _cfg("domain"),
                                  url_for('.connect_with_oauth_authorized_' + provider))
    return oauth.authorize(callback=callback)


@login_oauth.route("/disconnect-oauth", methods=['POST'])
def disconnect_oauth() -> werkzeug.wrappers.Response:
    provider = request.form.get('provider')
    assert provider in list_defined_oauths()  # This is a quick and dirty form of sanitation.
    auths = UserAuth.query.filter(UserAuth.provider == provider,
                                  UserAuth.user_id == current_user.id).all()
    for auth in auths:
        db.delete(auth)
    db.flush()  # So that /profile will display currectly
    return redirect('/profile/%s/edit' % current_user.username)


@login_oauth.route("/oauth/github/connect")
def connect_with_oauth_authorized_github() -> Union[str, werkzeug.wrappers.Response]:
    gh_user, _ = get_github_oath()
    return _connect_with_oauth_finalize(gh_user, 'github')


@login_oauth.route("/oauth/google/connect")
def connect_with_oauth_authorized_google() -> Union[str, werkzeug.wrappers.Response]:
    if 'code' not in request.args:
        # Got here in some strange scenario.
        return redirect('/')
    google = get_oauth_provider('google')
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    if 'error' in resp:
        return jsonify(resp)
    session['google_token'] = (resp['access_token'], '')
    google_info = google.get('userinfo')
    google_info = google_info.data
    google_user = google_info['id']  # This is a long number.
    return _connect_with_oauth_finalize(google_user, 'google')


@login_oauth.route("/oauth/github/login")
def login_with_oauth_authorized_github() -> Union[str, werkzeug.wrappers.Response]:
    gh_user, github = get_github_oath()
    auth = UserAuth.query.filter(
        UserAuth.provider == 'github',
        UserAuth.remote_user == gh_user).first()
    if auth:
        user = User.query.filter(User.id == auth.user_id).first()
        if user.confirmation:
            return redirect('/account-pending')
        login_user(user, remember=True)
        return redirect('/')
    else:
        emails = github.get('user/emails', [])
        emails = emails.data
        emails = [e['email'] for e in emails if e['primary']]
        if emails:
            email = emails[0]
        else:
            email = ''
        return render_register_with_oauth('github', gh_user, gh_user, email)


@login_oauth.route("/oauth/google/login")
def login_with_oauth_authorized_google() -> Union[str, werkzeug.wrappers.Response]:
    if 'code' not in request.args:
        # Got here in some strange scenario.
        return redirect('/')
    google = get_oauth_provider('google')
    resp = google.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    if 'error' in resp:
        return jsonify(resp.error)
    session['google_token'] = (resp['access_token'], '')
    google_info = google.get('userinfo')
    google_info = google_info.data
    google_user = google_info['id']  # This is a long number.
    auth = UserAuth.query.filter(
        UserAuth.provider == 'google',
        UserAuth.remote_user == google_user).first()
    if auth:
        user = User.query.filter(User.id == auth.user_id).first()
        if user.confirmation:
            return redirect('/account-pending')
        login_user(user, remember=True)
        return redirect('/')
    else:
        email = google_info['email']
        username = email[:email.find('@')]
        return render_register_with_oauth('google', google_user, username, email)


@login_oauth.route("/register-oauth", methods=['POST'])
def register_with_oauth_authorized() -> Union[str, werkzeug.wrappers.Response]:
    """
    This endpoint should be called after authorizing with oauth, by the user.
    """
    email = request.form.get('email', '')
    username = request.form.get('username', '')
    provider = request.form.get('provider', '')
    remote_user = request.form.get('remote_user', '')
    good = True
    if check_username_for_registration(username):
        good = False
    if check_email_for_registration(email):
        good = False
    if good:
        password = binascii.b2a_hex(os.urandom(99))
        user = User(username=username, email=email)
        user.set_password(str(password))
        user.create_confirmation()
        db.add(user)
        db.flush()  # to get an ID.
        auth = UserAuth(user_id=user.id,
                        remote_user=remote_user,
                        provider=provider)
        db.add(auth)
        db.commit()  # Commit before trying to email
        send_confirmation(user)
        return redirect("/account-pending")
    return render_register_with_oauth(provider, remote_user, username, email)


def render_register_with_oauth(provider: str, remote_user: str, username: str, email: str) -> str:
    provider_info = list_defined_oauths()[provider]
    parameters = {
        'email': email, 'username': username,
        'provider': provider,
        'provider_full_name': provider_info['full_name'],
        'provider_icon': provider_info['icon'],
        'remote_user': remote_user
    }
    error = check_username_for_registration(username)
    if error:
        parameters['usernameError'] = error
    error = check_email_for_registration(email)
    if error:
        parameters['emailError'] = error
    return render_template('register-oauth.html', **parameters)


def get_oauth_provider(provider: str) -> OAuthRemoteApp:
    oauth = OAuth(current_app)
    if provider == 'github':
        github = oauth.remote_app(
            'github',
            consumer_key=_cfg('gh-oauth-id'),
            consumer_secret=_cfg('gh-oauth-secret'),
            request_token_params={'scope': 'user:email'},
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize'
        )

        @github.tokengetter
        def get_github_oauth_token() -> str:
            return session.get('github_token', '')

        return github

    if provider == 'google':
        google = oauth.remote_app(
            'google',
            consumer_key=_cfg('google-oauth-id'),
            consumer_secret=_cfg('google-oauth-secret'),
            request_token_params={'scope': 'email'},
            base_url='https://www.googleapis.com/oauth2/v1/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
        )

        @google.tokengetter
        def get_google_oauth_token() -> str:
            return session.get('google_token', '')

        return google

    raise Exception('This OAuth provider was not implemented: ' + provider)
