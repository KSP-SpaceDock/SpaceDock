from flask import Blueprint, render_template, abort, request, redirect, session, url_for
from flask.ext.login import current_user, login_user, logout_user
from datetime import datetime, timedelta
from SpaceDock.email import send_confirmation, send_reset
from sqlalchemy import desc
from SpaceDock.objects import User, Mod, ModList, ModListItem, Game, Publisher
from SpaceDock.database import db
from SpaceDock.common import *
from SpaceDock.config import _cfg

import bcrypt
import re
import random
import base64
import binascii
import os

lists = Blueprint('lists', __name__, template_folder='../../templates/lists')

@lists.route("/create/pack")
def create_list():
    games = Game.query.filter(Game.active == True).order_by(desc(Game.id)).all()
    ga = Game.query.order_by(desc(Game.id)).first()
    return render_template("mods/create_list.html",game=games,ga=ga)
    
@lists.route("/pack/<int:list_id>/delete")
@loginrequired
@with_session
def delete(list_id):
    mod_list = ModList.query.filter(ModList.id == list_id).first()
    if not mod_list:
        abort(404)
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod_list.user_id:
            editable = True
    if not editable:
        abort(401)
    db.delete(mod_list)
    db.commit()
    return redirect("/profile/" + current_user.username)

@lists.route("/pack/<list_id>/<list_name>")
def view_list(list_id, list_name):
    mod_list = ModList.query.filter(ModList.id == list_id).first()
    ga = Game.query.filter(Game.id == mod_list.game_id).first()
    if not mod_list:
        abort(404)
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod_list.user_id:
            editable = True
    return render_template("mods/mod_list.html",
        **{
            'mod_list': mod_list,
            'editable': editable,
            'ga': ga
        })

@lists.route("/pack/<list_id>/<list_name>/edit", methods=['GET', 'POST'])
@with_session
@loginrequired
def edit_list(list_id, list_name):
    mod_list = ModList.query.filter(ModList.id == list_id).first()
    ga = Game.query.filter(Game.id == mod_list.game_id).first()
    if not mod_list:
        abort(404)
    editable = False
    if current_user:
        if current_user.admin:
            editable = True
        if current_user.id == mod_list.user_id:
            editable = True
    if not editable:
        abort(401)
    if request.method == 'GET':
        return render_template("mods/edit_list.html",
            **{
                'mod_list': mod_list,
                'mod_ids': [m.mod.id for m in mod_list.mods],
                'ga': ga
            })
    else:
        description = request.form.get('description')
        background = request.form.get('background')
        bgOffsetY = request.form.get('bg-offset-y')
        mods = json.loads(request.form.get('mods'))
        mod_list.description = description
        if background and background != '':
            mod_list.background = background
        try:
            mod_list.bgOffsetY = int(bgOffsetY)
        except:
            pass
        # Remove mods
        removed_mods = [m for m in mod_list.mods if not m.mod_id in mods]
        for mod in removed_mods:
            mod_list.mods.remove(mod)

        # Add mods
        added_mods = [m for m in mods if not m in [mod.mod.id for mod in mod_list.mods]]
        for m in added_mods:
            mod = Mod.query.filter(Mod.id == m).first()
            mli = ModListItem()
            mli.mod_id = mod.id
            mli.mod_list = mod_list
            mod_list.mods.append(mli)
            db.add(mli)
            db.commit()
        for mod in mod_list.mods:
            mod.sort_index = mods.index(mod.mod.id)
        return redirect(url_for("lists.view_list", list_id=mod_list.id, list_name=mod_list.name))
