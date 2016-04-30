from flask import Blueprint, render_template, abort, request, redirect, session, Response, send_from_directory, make_response, jsonify
from flask_login import current_user
from sqlalchemy import desc
from SpaceDock.objects import Featured, BlogPost, Mod, ModVersion, Publisher, Game
from SpaceDock.search import search_mods
from SpaceDock.common import *
from SpaceDock.config import _cfg
import os.path

import math
import json

anonymous = Blueprint('anonymous', __name__, template_folder='../../templates/anonymous')

@anonymous.route("/")
def index():
    games = Game.query.filter(Game.active == True).order_by(desc(Game.created))
    return render_template("index.html",\
        games=games)

@anonymous.route("/<gameshort>")
def game(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    if not ga:
        abort(404)
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    featured = Featured.query.outerjoin(Mod).filter(Mod.published,Mod.game_id == ga.id).order_by(desc(Featured.created)).limit(8)[:8]
    #top = search_mods("", 1, 3)[0]
    top = Mod.query.filter(Mod.published,Mod.game_id == ga.id).order_by(desc(Mod.download_count)).limit(6)[:6]
    new = Mod.query.filter(Mod.published,Mod.game_id == ga.id).order_by(desc(Mod.created)).limit(6)[:6]
    recent = Mod.query.filter(Mod.published,Mod.game_id == ga.id, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated)).limit(6)[:6]
    user_count = User.query.count()
    mod_count = Mod.query.filter(Mod.game_id == ga.id).count()
    yours = list()
    if current_user:
        yours = sorted(current_user.following, key=lambda m: m.updated, reverse=True)[:6]
    return render_template("game.html",\
        ga=ga,\
        featured=featured,\
        new=new,\
        top=top,\
        recent=recent,\
        user_count=user_count,\
        mod_count=mod_count,
        yours=yours)

@anonymous.route("/content/<path:path>")
def content(path):
    fullPath = _cfg('storage') + "/" +  path
    if not os.path.isfile(fullPath):
        abort(404)
    return send_from_directory(_cfg('storage') + "/", path)

@anonymous.route("/browse")
def browse():
    featured = Featured.query.order_by(desc(Featured.created)).limit(6)[:6]
    top = search_mods("", 1, 6)[:6][0]
    new = Mod.query.filter(Mod.published).order_by(desc(Mod.created)).limit(6)[:6]
    return render_template("mods/browse.html", featured=featured, top=top, new=new)

@anonymous.route("/browse/new")
def browse_new():
    mods = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    mods = mods.offset(30 * (page - 1)).limit(30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,\
            url="/browse/new", name="Newest Mods", rss="/browse/new.rss")

@anonymous.route("/browse/new.rss")
def browse_new_rss():
    mods = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
    mods = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="New mods on " + _cfg('site-name'),\
            description="The newest mods on " + _cfg('site-name'), \
            url="/browse/new"), mimetype="text/xml")

@anonymous.route("/browse/updated")
def browse_updated():
    mods = Mod.query.filter(Mod.published, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    mods = mods.offset(30 * (page - 1)).limit(30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,\
            url="/browse/updated", name="Recently Updated Mods", rss="/browse/updated.rss", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

@anonymous.route("/browse/updated.rss")
def browse_updated_rss():
    mods = Mod.query.filter(Mod.published, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="Recently updated on " + _cfg('site-name'),\
            description="Mods on " + _cfg('site-name') + " updated recently", \
            url="/browse/updated"), mimetype="text/xml")

@anonymous.route("/browse/top")
def browse_top():
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(False,"", page, 30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,\
            url="/browse/top", name="Popular Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

@anonymous.route("/browse/featured")
def browse_featured():
    mods = Featured.query.order_by(desc(Featured.created))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    if page != 0:
        mods = mods.offset(30 * (page - 1)).limit(30)
    mods = [f.mod for f in mods]
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,\
            url="/browse/featured", name="Featured Mods", rss="/browse/featured.rss")

@anonymous.route("/browse/featured.rss")
def browse_featured_rss():
    mods = Featured.query.order_by(desc(Featured.created))
    mods = mods.limit(30)
    # Fix dates
    for f in mods:
        f.mod.created = f.created
    mods = [dumb_object(f.mod) for f in mods]
    db.rollback()
    return Response(render_template("rss.xml", mods=mods, title="Featured mods on " + _cfg('site-name'),\
            description="Featured mods on " + _cfg('site-name'), \
            url="/browse/featured"), mimetype="text/xml")

@anonymous.route("/browse/all")
def browse_all():
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(False,"", page, 30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,\
            url="/browse/all", name="All Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

@anonymous.route("/<gameshort>/browse")
def singlegame_browse(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    featured = Featured.query.outerjoin(Mod).filter(Mod.game_id == ga.id).order_by(desc(Featured.created)).limit(6)[:6]
    top = search_mods(ga,"", 1, 6)[:6][0]
    new = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(desc(Mod.created)).limit(6)[:6]
    return render_template("mods/browse.html", featured=featured, top=top,ga = ga, new=new)

@anonymous.route("/<gameshort>/browse/new")
def singlegame_browse_new(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(desc(Mod.created))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    mods = mods.offset(30 * (page - 1)).limit(30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = ga,\
            url="/browse/new", name="Newest Mods", rss="/browse/new.rss")

@anonymous.route("/json/<gameshort>/browse/<path:r>")
@json_output
def json_singlegame_browse_new(gameshort,r):
    ra = r.split('/')
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    page = int(request.args.get('page'))
    na = ""
    rs = "/browse/all.rss"
    ru = ga.short + "/browse/all"
    if ra[0]:
        if ra[0].lower() == "new":
            mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(desc(Mod.created))
            na = "Newest Mods"
            rs = "/browse/new.rss"
            ru = ga.short + "/browse/new"
            total_pages = math.ceil(mods.count() / 30)
        elif ra[0].lower() == "updated":
            mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id,ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
            na = "Updated Mods"
            rs = "/browse/updated.rss"
            ru = ga.short + "/browse/updated"
            total_pages = math.ceil(mods.count() / 30)
        elif ra[0].lower() == "top":
            na = "Top Mods"
            rs = "/browse/top.rss"
            ru = ga.short + "/browse/top"
            mods = Mod.query.filter(Mod.game_id == ga.id).order_by(desc(Mod.follower_count))
            total_pages = math.ceil(mods.count() / 30)
        elif ra[0].lower() == "featured":
            mods = Mod.query.filter(Mod.game_id == ga.id).join(Featured).order_by(desc(Featured.created))
            na =" Featured Mods"
            rs = "/browse/featured.rss"
            ru = ga.short + "/browse/featured"
            total_pages = math.ceil(mods.count() / 30)
        else:
            mods = Mod.query.filter(Mod.game_id == ga.id).order_by(desc(Mod.follower_count))
            na = "All Mods"
            rs = "/browse/all.rss"
            ru = ga.short + "/browse/all"
            total_pages = math.ceil(mods.count() / 30)
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    
    mods = mods.offset(30 * (page - 1)).limit(30)
    mods = [e.serialize() for e in mods.all()]
    #modsj = jsonify([e.serialize() for e in mods.all()])
    #return { 'mods':mods, 'page':page, 'total_pages':total_pages,'ga':ga,'url':'/browse/new', 'name':'Newest Mods', 'rss':'/browse/new.rss'}
    #return { 'mods':modsj, 'page':page, 'total_pages':total_pages,'ga':ga,'url':'/browse/new', 'name':'Newest Mods', 'rss':'/browse/new.rss'}

    return jsonify({"page":page,"total_pages":total_pages,"url":ru, "name":na, "rss":rs,"mods":mods})

@anonymous.route("/<gameshort>/browse/new.rss")
def singlegame_browse_new_rss(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(desc(Mod.created))
    mods = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="New mods on " + _cfg('site-name'),ga = ga,\
            description="The newest mods on " + _cfg('site-name'), \
            url="/browse/new"), mimetype="text/xml")

@anonymous.route("/<gameshort>/browse/updated")
def singlegame_browse_updated(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    mods = Mod.query.filter(Mod.published,Mod.game_id == ga.id, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    mods = mods.offset(30 * (page - 1)).limit(30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = ga,\
            url="/browse/updated", name="Recently Updated Mods", rss="/browse/updated.rss", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

@anonymous.route("/<gameshort>/browse/updated.rss")
def singlegame_browse_updated_rss(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    mods = Mod.query.filter(Mod.published,Mod.game_id == ga.id, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="Recently updated on " + _cfg('site-name'),ga = ga,\
            description="Mods on " + _cfg('site-name') + " updated recently", \
            url="/browse/updated"), mimetype="text/xml")

@anonymous.route("/<gameshort>/browse/top")
def singlegame_browse_top(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(ga,"", page, 30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = ga,\
            url="/browse/top", name="Popular Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

@anonymous.route("/<gameshort>/browse/featured")
def singlegame_browse_featured(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    mods = Featured.query.outerjoin(Mod).filter(Mod.game_id == ga.id).order_by(desc(Featured.created))
    total_pages = math.ceil(mods.count() / 30)
    page = request.args.get('page')
    if page:
        page = int(page)
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
    else:
        page = 1
    if page != 0:
        mods = mods.offset(30 * (page - 1)).limit(30)
    mods = [f.mod for f in mods]
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages, ga = ga,\
            url="/browse/featured", name="Featured Mods", rss="/browse/featured.rss")

@anonymous.route("/<gameshort>/browse/featured.rss")
def singlegame_browse_featured_rss(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    mods = Featured.query.outerjoin(Mod).filter(Mod.game_id == ga.id).order_by(desc(Featured.created))
    mods = mods.limit(30)
    # Fix dates
    for f in mods:
        f.mod.created = f.created
    mods = [dumb_object(f.mod) for f in mods]
    db.rollback()
    return Response(render_template("rss.xml", mods=mods, title="Featured mods on " + _cfg('site-name'),ga = ga,\
            description="Featured mods on " + _cfg('site-name'), \
            url="/browse/featured"), mimetype="text/xml")

@anonymous.route("/<gameshort>/browse/all")
def singlegame_browse_all(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(False,"", page, 30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = ga,\
            url="/browse/all", name="All Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

@anonymous.route("/about")
def about():
    return render_template("static/about.html")

@anonymous.route("/markdown")
def markdown_info():
    return render_template("static/markdown.html")

@anonymous.route("/privacy")
def privacy():
    return render_template("static/privacy.html")

@anonymous.route("/voip")
def voip():
    return render_template("static/voip.html")

@anonymous.route("/chat")
def chat():
    return render_template("static/chat.html")

@anonymous.route("/donate")
def donate():
    return render_template("static/donate.html")

@anonymous.route("/search")
def search():
    query = request.args.get('query')
    if not query:
        query = ''
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(False,query, page, 30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages, search=True, query=query)

@anonymous.route("/<gameshort>/search")
def singlegame_search(gameshort):
    if not gameshort:
        gameshort = 'kerbal-space-program'
    ga = Game.query.filter(Game.short == gameshort).first()
    session['game'] = ga.id;
    session['gamename'] = ga.name;
    session['gameshort'] = ga.short;
    session['gameid'] = ga.id;
    query = request.args.get('query')
    if not query:
        query = ''
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    mods, total_pages = search_mods(ga,query, page, 30)
    return render_template("mods/browse-list.html", mods=mods, page=page, total_pages=total_pages, search=True, query=query,ga=ga)
