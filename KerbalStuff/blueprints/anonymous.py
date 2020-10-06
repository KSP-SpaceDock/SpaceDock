import os.path

from flask import Blueprint, render_template, send_from_directory, abort, request, Response
from flask_login import current_user
from sqlalchemy import desc
import werkzeug.wrappers

from ..common import dumb_object, paginate_mods, get_mods, get_game_info
from ..config import _cfg
from ..database import db
from ..objects import Featured, Mod, ModVersion, Game, User
from ..search import search_mods

anonymous = Blueprint('anonymous', __name__, template_folder='../../templates/anonymous')


@anonymous.route("/")
def index() -> str:
    games = Game.query.filter(Game.active == True).order_by(desc(Game.created))
    return render_template("index.html",
                           games=games)


@anonymous.route("/<gameshort>")
def game(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    featured = Featured.query.outerjoin(Mod).filter(
        Mod.published, Mod.game_id == ga.id).order_by(desc(Featured.created)).limit(6)[:6]
    # top = search_mods("", 1, 3)[0]
    top = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(
        desc(Mod.download_count)).limit(6)[:6]
    new = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(
        desc(Mod.created)).limit(6)[:6]
    recent = Mod.query.filter(Mod.published, Mod.game_id == ga.id, ModVersion.query.filter(
        ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated)).limit(6)[:6]
    user_count = User.query.count()
    mod_count = Mod.query.filter(Mod.game_id == ga.id, Mod.published == True).count()
    yours = list()
    if current_user:
        yours = sorted(filter(lambda m: m.game_id == ga.id, current_user.following),
            key=lambda m: m.updated, reverse=True)[:6]
    return render_template("game.html",
                           ga=ga,
                           featured=featured,
                           new=new,
                           top=top,
                           recent=recent,
                           user_count=user_count,
                           mod_count=mod_count,
                           yours=yours)


@anonymous.route("/content/<path:path>")
def content(path: str) -> werkzeug.wrappers.Response:
    storage = _cfg('storage')
    if not storage or not os.path.isfile(os.path.join(storage, path)):
        abort(404)
    return send_from_directory(storage + "/", path)


@anonymous.route("/browse")
def browse() -> str:
    featured = Featured.query.order_by(desc(Featured.created)).limit(6).all()
    top = search_mods(None, '', 1, 6)[0]
    new = Mod.query.filter(Mod.published).order_by(desc(Mod.created)).limit(6).all()
    return render_template("browse.html", featured=featured, top=top, new=new)


@anonymous.route("/browse/new")
def browse_new() -> str:
    mods = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
    mods, page, total_pages = paginate_mods(mods)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/new", name="Newest Mods", rss="/browse/new.rss")


@anonymous.route("/browse/new.rss")
def browse_new_rss() -> Response:
    mods = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
    mods = mods.limit(30)
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)
    return Response(render_template("rss.xml", mods=mods, title="New mods on " + site_name,
                                    description="The newest mods on " + site_name,
                                    url="/browse/new"), mimetype="text/xml")


@anonymous.route("/browse/updated")
def browse_updated() -> str:
    mods = Mod.query.filter(Mod.published, ModVersion.query.filter(
        ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods, page, total_pages = paginate_mods(mods)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/updated", name="Recently Updated Mods", rss="/browse/updated.rss", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/browse/updated.rss")
def browse_updated_rss() -> Response:
    mods = Mod.query.filter(Mod.published, ModVersion.query.filter(
        ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods = mods.limit(30)
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)
    return Response(render_template("rss.xml", mods=mods, title="Recently updated on " + site_name,
                                    description="Mods on " +
                                    site_name + " updated recently",
                                    url="/browse/updated"), mimetype="text/xml")


@anonymous.route("/browse/top")
def browse_top() -> str:
    mods, page, total_pages = get_mods()
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/top", name="Popular Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/browse/featured")
def browse_featured() -> str:
    mods = Featured.query.order_by(desc(Featured.created))
    mods, page, total_pages = paginate_mods(mods)
    mods = [f.mod for f in mods]
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/featured", name="Featured Mods", rss="/browse/featured.rss")


@anonymous.route("/browse/featured.rss")
def browse_featured_rss() -> Response:
    mods = Featured.query.order_by(desc(Featured.created))
    mods = mods.limit(30)
    # Fix dates
    for f in mods:
        f.mod.created = f.created
    mods = [dumb_object(f.mod) for f in mods]
    db.rollback()
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)
    return Response(render_template("rss.xml", mods=mods, title="Featured mods on " + site_name,
                                    description="Featured mods on " + site_name,
                                    url="/browse/featured"), mimetype="text/xml")


@anonymous.route("/browse/all")
def browse_all() -> str:
    mods, page, total_pages = get_mods()
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/all", name="All Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/<gameshort>/browse")
def singlegame_browse(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    featured = Featured.query.outerjoin(Mod).filter(
        Mod.game_id == ga.id).order_by(desc(Featured.created)).limit(6).all()
    top = search_mods(ga, "", 1, 6)[0]
    new = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(
        desc(Mod.created)).limit(6).all()
    return render_template("browse.html", featured=featured, top=top, ga=ga, new=new)


@anonymous.route("/<gameshort>/browse/new")
def singlegame_browse_new(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(desc(Mod.created))
    mods, page, total_pages = paginate_mods(mods)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, ga=ga,
                           url="/browse/new", name="Newest Mods", rss="/browse/new.rss")


@anonymous.route("/<gameshort>/browse/new.rss")
def singlegame_browse_new_rss(gameshort: str) -> Response:
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)
    ga = get_game_info(short=gameshort)
    mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id).order_by(desc(Mod.created))
    mods = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="New mods on " + site_name, ga=ga,
                                    description="The newest mods on " + site_name,
                                    url="/browse/new"), mimetype="text/xml")


@anonymous.route("/<gameshort>/browse/updated")
def singlegame_browse_updated(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id, ModVersion.query.filter(
        ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods, page, total_pages = paginate_mods(mods)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, ga=ga,
                           url="/browse/updated", name="Recently Updated Mods", rss="/browse/updated.rss", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/<gameshort>/browse/updated.rss")
def singlegame_browse_updated_rss(gameshort: str) -> Response:
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)
    ga = get_game_info(short=gameshort)
    mods = Mod.query.filter(Mod.published, Mod.game_id == ga.id, ModVersion.query.filter(
        ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="Recently updated on " + site_name, ga=ga,
                                    description="Mods on " +
                                    site_name + " updated recently",
                                    url="/browse/updated"), mimetype="text/xml")


@anonymous.route("/<gameshort>/browse/top")
def singlegame_browse_top(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    mods, page, total_pages = get_mods(ga)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, ga=ga,
                           url="/browse/top", name="Popular Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/<gameshort>/browse/featured")
def singlegame_browse_featured(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    mods = Featured.query.outerjoin(Mod).filter(
        Mod.game_id == ga.id).order_by(desc(Featured.created))
    mods, page, total_pages = paginate_mods(mods)
    mods = [f.mod for f in mods]
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, ga=ga,
                           url="/browse/featured", name="Featured Mods", rss="/browse/featured.rss")


@anonymous.route("/<gameshort>/browse/featured.rss")
def singlegame_browse_featured_rss(gameshort: str) -> Response:
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)
    ga = get_game_info(short=gameshort)
    mods = Featured.query.outerjoin(Mod).filter(
        Mod.game_id == ga.id).order_by(desc(Featured.created))
    mods = mods.limit(30)
    # Fix dates
    for f in mods:
        f.mod.created = f.created
    mods = [dumb_object(f.mod) for f in mods]
    db.rollback()
    return Response(render_template("rss.xml", mods=mods, title="Featured mods on " + site_name, ga=ga,
                                    description="Featured mods on " + site_name,
                                    url="/browse/featured"), mimetype="text/xml")


@anonymous.route("/<gameshort>/browse/all")
def singlegame_browse_all(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    mods, page, total_pages = get_mods(ga)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, ga=ga,
                           url="/browse/all", name="All Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/about")
def about() -> str:
    return render_template("about.html")


@anonymous.route("/markdown")
def markdown_info() -> str:
    return render_template("markdown.html")


@anonymous.route("/privacy")
def privacy() -> str:
    return render_template("privacy.html")


@anonymous.route("/search")
def search() -> str:
    query = request.args.get('query') or ''
    mods, page, total_pages = get_mods(query=query)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, search=True, query=query)


@anonymous.route("/<gameshort>/search")
def singlegame_search(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    query = request.args.get('query') or ''
    mods, page, total_pages = get_mods(ga, query)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, search=True, query=query, ga=ga)
