import os.path
import time

from flask import Blueprint, render_template, send_from_directory, abort, request, Response
from flask_login import current_user
from sqlalchemy import desc

from ..common import dumb_object, paginate_mods, get_page, get_mods, get_game_info
from ..config import _cfg
from ..database import db
from ..objects import Featured, Mod, ModVersion, Game, User
from ..search import search_mods

cache_time = 60
anonymous = Blueprint('anonymous', __name__, template_folder='../../templates/anonymous')


@anonymous.route("/")
def index():
    games = Game.query.filter(Game.active == True).order_by(desc(Game.created))
    return render_template("index.html",
        games=games)

gameshort_cache = {}
@anonymous.route("/<gameshort>")
def game(gameshort):
    global gameshort_cache
    currentTime = time.time()
    if (not gameshort in gameshort_cache):
        gameshort_cache[gameshort] = {}
        gameshort_cache[gameshort]['time'] = 0
    current_cache = gameshort_cache[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        current_cache['featured'] = Featured.query.outerjoin(Mod).filter(Mod.published,Mod.game_id == current_cache['ga'].id).order_by(desc(Featured.created)).limit(6)[:6]
        # top = search_mods("", 1, 3)[0]
        current_cache['top'] = Mod.query.filter(Mod.published,Mod.game_id == current_cache['ga'].id).order_by(desc(Mod.download_count)).limit(6)[:6]
        current_cache['new'] = Mod.query.filter(Mod.published,Mod.game_id == current_cache['ga'].id).order_by(desc(Mod.created)).limit(6)[:6]
        current_cache['recent'] = Mod.query.filter(Mod.published,Mod.game_id == current_cache['ga'].id, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated)).limit(6)[:6]
        gameshort_cache['user_count'] = User.query.count()
        current_cache['mod_count'] = Mod.query.filter(Mod.game_id == current_cache['ga'].id).count()
        
    yours = list()
    if current_user:
        yours = sorted(current_user.following, key=lambda m: m.updated, reverse=True)[:6]
    return render_template("game.html",
                           ga=current_cache['ga'],
                           featured=current_cache['featured'],
                           new=current_cache['new'],
                           top=current_cache['top'],
                           recent=current_cache['recent'],
                           user_count=gameshort_cache['user_count'],
                           mod_count=current_cache['mod_count'],
                           yours=yours)


@anonymous.route("/content/<path:path>")
def content(path):
    if not os.path.isfile(os.path.join(_cfg('storage'), path)):
        abort(404)
    return send_from_directory(_cfg('storage') + "/", path)


browse_cache = {}
browse_cache['time'] = 0
@anonymous.route("/browse")
def browse():
    global browse_cache
    currentTime = time.time()
    if (currentTime - browse_cache['time'] > cache_time):
        browse_cache['time'] = currentTime
        browse_cache['featured'] = Featured.query.order_by(desc(Featured.created)).limit(6).all()
        browse_cache['top'] = search_mods(None, '', 1, 6)[0]
        browse_cache['new'] = Mod.query.filter(Mod.published).order_by(desc(Mod.created)).limit(6).all()
    return render_template("browse.html", featured=browse_cache['featured'], top=browse_cache['top'], new=browse_cache['new'])

new_cache = {}
new_cache['time'] = 0
@anonymous.route("/browse/new")
def browse_new():
    global new_cache
    currentTime = time.time()
    if (currentTime - new_cache['time'] > cache_time):
        new_cache['time'] = currentTime
        new_cache['mods'] = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
    mods, page, total_pages = paginate_mods(new_cache['mods'])
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/new", name="Newest Mods", rss="/browse/new.rss")

new_cache_rss = {}
new_cache_rss['time'] = 0
@anonymous.route("/browse/new.rss")
def browse_new_rss():
    global new_cache_rss
    currentTime = time.time()
    if (currentTime - new_cache_rss['time'] > cache_time):
        new_cache_rss['time'] = currentTime
        mods = Mod.query.filter(Mod.published).order_by(desc(Mod.created))
        new_cache_rss['mods'] = mods.limit(30)
    return Response(render_template("rss.xml", mods=new_cache_rss['mods'], title="New mods on " + _cfg('site-name'),
                                    description="The newest mods on " + _cfg('site-name'),
                                    url="/browse/new"), mimetype="text/xml")

updated_cache = {}
updated_cache['time'] = 0
@anonymous.route("/browse/updated")
def browse_updated():
    global updated_cache
    currentTime = time.time()
    if (currentTime - updated_cache['time'] > cache_time):
        updated_cache['time'] = currentTime
        updated_cache['mods'] = Mod.query.filter(Mod.published, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods, page, total_pages = paginate_mods(updated_cache['mods'])
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/updated", name="Recently Updated Mods", rss="/browse/updated.rss", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

updated_cache_rss = {}
updated_cache_rss['time'] = 0
@anonymous.route("/browse/updated.rss")
def browse_updated_rss():
    global updated_cache_rss
    currentTime = time.time()
    if (currentTime - updated_cache_rss['time'] > cache_time):
        updated_cache_rss['time'] = currentTime
        mods = Mod.query.filter(Mod.published, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
        updated_cache_rss['mods'] = mods.limit(30)
    return Response(render_template("rss.xml", mods=updated_cache_rss['mods'], title="Recently updated on " + _cfg('site-name'),
                                    description="Mods on " + _cfg('site-name') + " updated recently",
                                    url="/browse/updated"), mimetype="text/xml")

top_cache = {}
top_cache['time'] = 0
@anonymous.route("/browse/top")
def browse_top():
    page = request.args.get('page')
    if page:
        page = int(page)
    else:
        page = 1
    if (page == 1):
        global top_cache
        currentTime = time.time()
        if (currentTime - top_cache['time'] > cache_time):
            top_cache['time'] = currentTime
            top_cache['mods'], top_cache['total_pages'] = search_mods(None, "", page, 30)
        mods = top_cache['mods']
        total_pages = top_cache['total_pages']
    else:
        mods, total_pages = search_mods(None, "", page, 30)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/top", name="Popular Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


featured_cache = {}
featured_cache['time'] = 0
@anonymous.route("/browse/featured")
def browse_featured():
    global featured_cache
    currentTime = time.time()
    if (currentTime - featured_cache['time'] > cache_time):
        featured_cache['time'] = currentTime
        featured_cache['mods'] = Featured.query.order_by(desc(Featured.created))
    mods, page, total_pages = paginate_mods(featured_cache['mods'])
    mods = [f.mod for f in mods]
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,
                           url="/browse/featured", name="Featured Mods", rss="/browse/featured.rss")

featured_cache_rss = {}
featured_cache_rss['time'] = 0
@anonymous.route("/browse/featured.rss")
def browse_featured_rss():
    global featured_cache_rss
    currentTime = time.time()
    if (currentTime - featured_cache_rss['time'] > cache_time):
        featured_cache_rss['time'] = currentTime
        mods = Featured.query.order_by(desc(Featured.created))
        mods = mods.limit(30)
        # Fix dates
        for f in mods:
            f.mod.created = f.created
        mods = [dumb_object(f.mod) for f in mods]
        db.rollback()
        featured_cache_rss['mods'] = mods
    return Response(render_template("rss.xml", mods=featured_cache_rss['mods'], title="Featured mods on " + _cfg('site-name'),
                                    description="Featured mods on " + _cfg('site-name'),
                                    url="/browse/featured"), mimetype="text/xml")

#TODO: We can't cache mods here. Needs to be cached in get_mods
@anonymous.route("/browse/all")
def browse_all():
    mods, page, total_pages = get_mods()
    return render_template("browse-list.html", mods=mods, page=get_page(), total_pages=total_pages,
                           url="/browse/all", name="All Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

gameshort_browse_cache = {}
gameshort_browse_cache['time'] = 0
@anonymous.route("/<gameshort>/browse")
def singlegame_browse(gameshort):
    global gameshort_browse_cache
    currentTime = time.time()
    if (not gameshort in gameshort_browse_cache):
        gameshort_browse_cache[gameshort] = {}
        gameshort_browse_cache[gameshort]['time'] = 0
    current_cache = gameshort_browse_cache[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        current_cache['featured'] = Featured.query.outerjoin(Mod).filter(Mod.game_id == current_cache['ga'].id).order_by(desc(Featured.created)).limit(6)[:6]
        current_cache['top'] = search_mods(current_cache['ga'], "", 1, 6)[0][:6]
        current_cache['new'] = Mod.query.filter(Mod.published, Mod.game_id == current_cache['ga'].id).order_by(desc(Mod.created)).limit(6).all()
    return render_template("browse.html", featured=current_cache['featured'], top=current_cache['top'], ga=current_cache['ga'], new=current_cache['new'])


gameshort_new_cache = {}
gameshort_new_cache['time'] = 0
@anonymous.route("/<gameshort>/browse/new")
def singlegame_browse_new(gameshort):
    global gameshort_new_cache
    currentTime = time.time()
    if (not gameshort in gameshort_new_cache):
        gameshort_new_cache[gameshort] = {}
        gameshort_new_cache[gameshort]['time'] = 0
    current_cache = gameshort_new_cache[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        current_cache['mods'] = Mod.query.filter(Mod.published, Mod.game_id == current_cache['ga'].id).order_by(desc(Mod.created))
    mods, page, total_pages = paginate_mods(current_cache['mods'])
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = current_cache['ga'],
                           url="/browse/new", name="Newest Mods", rss="/browse/new.rss")

gameshort_new_cache_rss = {}
gameshort_new_cache_rss['time'] = 0
@anonymous.route("/<gameshort>/browse/new.rss")
def singlegame_browse_new_rss(gameshort):
    global gameshort_new_cache_rss
    currentTime = time.time()
    if (not gameshort in gameshort_new_cache_rss):
        gameshort_new_cache_rss[gameshort] = {}
        gameshort_new_cache_rss[gameshort]['time'] = 0
    current_cache = gameshort_new_cache_rss[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        mods = Mod.query.filter(Mod.published, Mod.game_id == current_cache['ga'].id).order_by(desc(Mod.created))
        current_cache['mods'] = mods.limit(30)
    return Response(render_template("rss.xml", mods=current_cache['mods'], title="New mods on " + _cfg('site-name'),ga = current_cache['ga'],
                                    description="The newest mods on " + _cfg('site-name'),
                                    url="/browse/new"), mimetype="text/xml")

gameshort_updated_cache = {}
gameshort_updated_cache['time'] = 0
@anonymous.route("/<gameshort>/browse/updated")
def singlegame_browse_updated(gameshort):
    global gameshort_updated_cache
    currentTime = time.time()
    if (not gameshort in gameshort_updated_cache):
        gameshort_updated_cache[gameshort] = {}
        gameshort_updated_cache[gameshort]['time'] = 0
    current_cache = gameshort_updated_cache[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        current_cache['mods'] = Mod.query.filter(Mod.published,Mod.game_id == current_cache['ga'].id, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    mods, page, total_pages = paginate_mods(current_cache['mods'])
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = current_cache['ga'],
                           url="/browse/updated", name="Recently Updated Mods", rss="/browse/updated.rss", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

gameshort_updated_cache_rss = {}
gameshort_updated_cache_rss['time'] = 0
@anonymous.route("/<gameshort>/browse/updated.rss")
def singlegame_browse_updated_rss(gameshort):
    global gameshort_updated_cache
    currentTime = time.time()
    if (not gameshort in gameshort_updated_cache):
        gameshort_updated_cache[gameshort] = {}
        gameshort_updated_cache[gameshort]['time'] = 0
    current_cache = gameshort_updated_cache[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
    current_cache['ga'] = get_game_info(short=gameshort)
    mods = Mod.query.filter(Mod.published,Mod.game_id == current_cache['ga'].id, ModVersion.query.filter(ModVersion.mod_id == Mod.id).count() > 1).order_by(desc(Mod.updated))
    current_cache['mods'] = mods.limit(30)
    return Response(render_template("rss.xml", mods=mods, title="Recently updated on " + _cfg('site-name'),ga = current_cache['ga'],
                                    description="Mods on " + _cfg('site-name') + " updated recently",
                                    url="/browse/updated"), mimetype="text/xml")


gameshort_top_cache = {}
gameshort_top_cache['time'] = 0
@anonymous.route("/<gameshort>/browse/top")
def singlegame_browse_top(gameshort):
    page = get_page()
    if (page == 1):
        global gameshort_top_cache
        currentTime = time.time()
        if (not gameshort in gameshort_top_cache):
            gameshort_top_cache[gameshort] = {}
            gameshort_top_cache[gameshort]['time'] = 0
        current_cache = gameshort_top_cache[gameshort]
        if (currentTime - current_cache['time'] > cache_time):
            current_cache['time'] = currentTime
            current_cache['ga'] = get_game_info(short=gameshort)
            current_cache['mods'], page, current_cache['total_pages'] = get_mods(current_cache['ga'])
        mods = current_cache['mods']
        total_pages = current_cache['total_pages']
    else:
        ga = get_game_info(short=gameshort)
        mods, page, total_pages = get_mods(ga)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = current_cache['ga'],
                           url="/browse/top", name="Popular Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))

gameshort_featured_cache = {}
gameshort_featured_cache['time'] = 0
@anonymous.route("/<gameshort>/browse/featured")
def singlegame_browse_featured(gameshort):
    global gameshort_featured_cache
    currentTime = time.time()
    if (not gameshort in gameshort_featured_cache):
        gameshort_featured_cache[gameshort] = {}
        gameshort_featured_cache[gameshort]['time'] = 0
    current_cache = gameshort_featured_cache[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        current_cache['mods'] = Featured.query.outerjoin(Mod).filter(Mod.game_id == current_cache['ga'].id).order_by(desc(Featured.created))
    mods, page, total_pages = paginate_mods(current_cache['mods'])
    mods = [f.mod for f in mods]
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, ga = current_cache['ga'],
                           url="/browse/featured", name="Featured Mods", rss="/browse/featured.rss")

gameshort_featured_cache_rss = {}
gameshort_featured_cache_rss['time'] = 0
@anonymous.route("/<gameshort>/browse/featured.rss")
def singlegame_browse_featured_rss(gameshort):
    global gameshort_featured_cache_rss
    currentTime = time.time()
    if (not gameshort in gameshort_featured_cache_rss):
        gameshort_featured_cache_rss[gameshort] = {}
        gameshort_featured_cache_rss[gameshort]['time'] = 0
    current_cache = gameshort_featured_cache_rss[gameshort]
    if (currentTime - current_cache['time'] > cache_time):
        current_cache['time'] = currentTime
        current_cache['ga'] = get_game_info(short=gameshort)
        mods = Featured.query.outerjoin(Mod).filter(Mod.game_id == current_cache['ga'].id).order_by(desc(Featured.created))
        mods = mods.limit(30)
        # Fix dates
        for f in mods:
            f.mod.created = f.created
        current_cache['mods'] = [dumb_object(f.mod) for f in mods]
        db.rollback()
    return Response(render_template("rss.xml", mods=current_cache['mods'], title="Featured mods on " + _cfg('site-name'),ga = current_cache['ga'],
                                    description="Featured mods on " + _cfg('site-name'),
                                    url="/browse/featured"), mimetype="text/xml")


#TODO: We can't cache mods here. Needs to be cached in get_mods
@anonymous.route("/<gameshort>/browse/all")
def singlegame_browse_all(gameshort):
    ga = get_game_info(short=gameshort)
    mods, page, total_pages = get_mods(ga)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages,ga = ga,
                           url="/browse/all", name="All Mods", site_name=_cfg('site-name'), support_mail=_cfg('support-mail'))


@anonymous.route("/about")
def about():
    return render_template("about.html")


@anonymous.route("/markdown")
def markdown_info():
    return render_template("markdown.html")


@anonymous.route("/privacy")
def privacy():
    return render_template("privacy.html")


@anonymous.route("/search")
def search():
    query = request.args.get('query') or ''
    mods, page, total_pages = get_mods(query=query)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, search=True, query=query)


@anonymous.route("/<gameshort>/search")
def singlegame_search(gameshort):
    ga = get_game_info(short=gameshort)
    query = request.args.get('query') or ''
    mods, page, total_pages = get_mods(ga, query)
    return render_template("browse-list.html", mods=mods, page=page, total_pages=total_pages, search=True, query=query,ga=ga)
