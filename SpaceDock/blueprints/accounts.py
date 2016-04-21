from flask import Blueprint, render_template, abort, request, redirect, session
from flask.ext.login import current_user, login_user, logout_user
from datetime import datetime, timedelta
from SpaceDock.email import send_confirmation, send_reset
from SpaceDock.objects import User, Mod
from SpaceDock.database import db
from SpaceDock.common import *
from SpaceDock.config import _cfg, _cfgi, _cfgb

import bcrypt
import re
import random
import base64
import binascii
import os

accounts = Blueprint('accounts', __name__, template_folder='../../templates/accounts')

@accounts.route("/register", methods=['GET','POST'])
@with_session
def register():
    if not _cfgb('registration'):
        return redirect("/")
    if request.method == 'POST':
        # Validate
        kwargs = dict()
        followMod = request.form.get('follow-mod')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmPassword = request.form.get('repeatPassword')



        error = check_email_for_registration(email)
        if error:
            kwargs['emailError'] = error

        error = check_username_for_registration(username)
        if error:
            kwargs['usernameError'] = error

        if not password:
            kwargs['passwordError'] = 'Password is required.'
        else:
            if password != confirmPassword:
                kwargs['repeatPasswordError'] = 'Passwords do not match.'
            if len(password) < 5:
                kwargs['passwordError'] = 'Your password must be greater than 5 characters.'
            if len(password) > 256:
                kwargs['passwordError'] = 'We admire your dedication to security, but please use a shorter password.'
        if not kwargs == dict():
            if email is not None:
                kwargs['email'] = email
            if username is not None:
                kwargs['username'] = username
            kwargs['registration'] = registration = _cfgb('registration')
            print("test")
            return render_template("register.html", **kwargs)
        # All valid, let's make them an account
        user = User(username, email, password)
        user.confirmation = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
        db.add(user)
        db.commit() # We do this manually so that we're sure everything's hunky dory before the email leaves
        if followMod:
            send_confirmation(user, followMod)
        else:
            send_confirmation(user)
        return redirect("/account-pending")
    else:
        return render_template("register.html", registration=_cfgb('registration'))


def check_username_for_registration(username):
    if not username:
        return 'Username is required.'
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return 'Please only use letters, numbers, and underscores.'
    if len(username) < 3 or len(username) > 24:
        return 'Usernames must be between 3 and 24 characters.'
    if db.query(User).filter(User.username.ilike(username)).first():
        return 'A user by this name already exists.'
    return None

def check_email_for_registration(email):
    if not email:
        return 'Email is required.'
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return 'Please specify a valid email address.'
    elif db.query(User).filter(User.email == email).first():
        return 'A user with this email already exists.'
    return None


@accounts.route("/account-pending")
def account_pending():
    return render_template("account-pending.html", activation_mail=_cfg('activation-mail'))

@accounts.route("/confirm/<username>/<confirmation>")
@with_session
def confirm(username, confirmation):
    user = User.query.filter(User.username == username).first()
    if user and user.confirmation == None:
        return redirect("/")
    if not user or user.confirmation != confirmation:
        return render_template("confirm.html", success=False, user=user)
    else:
        user.confirmation = None
        login_user(user)
        f = request.args.get('f')
        if f:
            mod = Mod.query.filter(Mod.id == int(f)).first()
            mod.follower_count += 1
            user.following.append(mod)
            return render_template("confirm.html", success=True, user=user, followed=mod)
        else:
            return render_template("confirm.html", success=True, user=user)

@accounts.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user:
            return redirect("/")
        reset = request.args.get('reset') == '1'
        return render_template("login.html", return_to=request.args.get('return_to'), reset=reset)
    else:
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember-me')
        if remember == "on":
            remember = True
        else:
            remember = False
        user = User.query.filter(User.username.ilike(username)).first()
        if not user:
            return render_template("login.html", username=username, errors='Your username or password is incorrect.')
        if user.confirmation != '' and user.confirmation != None:
            return redirect("/account-pending")
        if not bcrypt.hashpw(password.encode('utf-8'), user.password.encode('utf-8')) == user.password.encode('utf-8'):
            return render_template("login.html", username=username, errors='Your username or password is incorrect.')
        login_user(user, remember=remember)
        if 'return_to' in request.form and request.form['return_to']:
            return redirect(urllib.parse.unquote(request.form.get('return_to')))
        return redirect("/")

@accounts.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@accounts.route("/forgot-password", methods=['GET', 'POST'])
@with_session
def forgot_password():
    if request.method == 'GET':
        return render_template("forgot.html")
    else:
        email = request.form.get('email')
        if not email:
            return render_template("forgot.html", bad_email=True)
        user = User.query.filter(User.email == email).first()
        if not user:
            return render_template("forgot.html", bad_email=True, email=email)
        user.passwordReset = binascii.b2a_hex(os.urandom(20)).decode("utf-8")
        user.passwordResetExpiry = datetime.now() + timedelta(days=1)
        db.commit()
        send_reset(user)
        return render_template("forgot.html", success=True)

@accounts.route("/reset", methods=['GET', 'POST'])
@accounts.route("/reset/<username>/<confirmation>", methods=['GET', 'POST'])
@with_session
def reset_password(username, confirmation):
    user = User.query.filter(User.username == username).first()
    if not user:
        redirect("/")
    if request.method == 'GET':
        if user.passwordResetExpiry == None or user.passwordResetExpiry < datetime.now():
            return render_template("reset.html", expired=True)
        if user.passwordReset != confirmation:
            redirect("/")
        return render_template("reset.html", username=username, confirmation=confirmation)
    else:
        if user.passwordResetExpiry == None or user.passwordResetExpiry < datetime.now():
            abort(401)
        if user.passwordReset != confirmation:
            abort(401)
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if not password or not password2:
            return render_template("reset.html", username=username, confirmation=confirmation, errors="Please fill out both fields.")
        if password != password2:
            return render_template("reset.html", username=username, confirmation=confirmation, errors="You seem to have mistyped one of these, please try again.")
        user.set_password(password)
        user.passwordReset = None
        user.passwordResetExpiry = None
        db.commit()
        return redirect("/login?reset=1")
