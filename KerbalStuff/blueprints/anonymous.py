
import os.path
from datetime import timezone

import werkzeug.wrappers
from flask import (
    Blueprint,
    render_template,
    abort,
    request,
    Response,
    redirect,
)
from flask_login import current_user

from ..common import (
    dumb_object,
    paginate_query,
    get_paginated_mods,
    get_game_info,
    get_games,
    get_featured_mods,
    get_top_mods,
    get_new_mods,
    get_updated_mods,
    sendfile,
)
from ..config import _cfg
from ..database import db
from ..objects import (
    Featured,
    Mod,
    ModVersion,
    User,
    ModList,
    ModCategory,
    GameModCategory,
)
from ..search import apply_search_to_query

anonymous = Blueprint('anonymous', __name__)

def get_game_category(gameshort: str, modcategory: str):
    """Return an enabled category belonging to the requested game."""
    ga = get_game_info(short=gameshort)

    setting = (
        GameModCategory.query
        .join(GameModCategory.category)
        .filter(
            GameModCategory.game_id == ga.id,
            GameModCategory.enabled.is_(True),
            ModCategory.stub == modcategory,
        )
        .first()
    )

    if setting is None or setting.category is None:
        abort(404)

    return ga, setting.category



@anonymous.route("/")
def index() -> str:
    return render_template("index.html", games=get_games())




@anonymous.route("/<gameshort>/<modcategory>")
def game_category(gameshort: str, modcategory: str) -> str:
    ga, category = get_game_category(gameshort, modcategory)

    category = ModCategory.query.filter_by(stub=modcategory).first()
    if category is None:
        abort(404)

    mods = Mod.query.filter(
        Mod.game_id == ga.id,
        Mod.category_id == category.id,
        Mod.published.is_(True),
    )

    featured = (
        Featured.query
        .join(Featured.mod)
        .filter(
            Mod.game_id == ga.id,
            Mod.category_id == category.id,
            Mod.published.is_(True),
        )
        .order_by(Featured.priority.desc())
        .limit(6)
        .all()
    )

    top = mods.order_by(Mod.score.desc()).limit(6).all()
    new = mods.order_by(Mod.created.desc()).limit(6).all()

    recent = (
        mods.filter(
            Mod.versions.any(
                ModVersion.id != Mod.default_version_id
            )
        )
        .order_by(Mod.updated.desc())
        .limit(6)
        .all()
    )

    user_count = User.query.count()
    mod_count = mods.count()

    pack_count = ModList.query.filter(
        ModList.game_id == ga.id,
        ModList.mods.any(),
    ).count()

    # Anonymous visitors should not need a user object.
    following = []
    user = None
    logged_in = False

    try:
        user = current_user
        logged_in = (
            user is not None
            and bool(user.is_authenticated)
        )
    except (AttributeError, TypeError):
        user = None
        logged_in = False

    if logged_in and user is not None:
        following = sorted(
            (
                mod for mod in user.following
                if mod.game_id == ga.id
                and mod.category_id == category.id
            ),
            key=lambda mod: mod.updated,
            reverse=True,
        )[:6]

    return render_template(
        "game.html",
        ga=ga,
        category=category,
        background=ga.background_url(
            _cfg('protocol'),
            _cfg('cdn-domain'),
        ),
        editable=bool(
            logged_in
            and user is not None
            and user.admin
        ),
        featured=featured,
        new=new,
        top=top,
        recent=recent,
        user_count=user_count,
        mod_count=mod_count,
        pack_count=pack_count,
        yours=following,
    )

@anonymous.route("/<gameshort>")
def game(gameshort: str) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}",
        code=301,
    )


@anonymous.route("/<gameshort>/background")
def game_background(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    if not ga.background:
        abort(404)

    return sendfile(ga.background, False)


@anonymous.route("/<gameshort>/thumb")
def game_thumbnail(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    if not ga.thumbnail:
        abort(404)

    return sendfile(ga.thumbnail, False)


@anonymous.route("/content/<path:path>")
def content(path: str) -> werkzeug.wrappers.Response:
    storage = _cfg('storage')
    if not storage:
        abort(404)

    return sendfile(path, True)

# legacy routes have nowwhere to go because we are missing important params.
@anonymous.route("/browse/new")
@anonymous.route("/browse/new.rss")
@anonymous.route("/browse/updated")
@anonymous.route("/browse/updated.rss")
@anonymous.route("/browse/top")
@anonymous.route("/browse/featured")
@anonymous.route("/browse/all")
@anonymous.route("/browse/featured.rss")
@anonymous.route("/browse/new")
@anonymous.route("/browse")
def browse() -> str:
    return redirect(
        f"/",
        code=301,
    )

@anonymous.route("/<gameshort>/<modcategory>/browse")
def singlegame_browse_category(
    gameshort: str,
    modcategory: str,
) -> str:
    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    featured = get_featured_mods(ga.id, 6)
    top = get_top_mods(ga.id, 6)
    new = get_new_mods(ga.id, 6)

    featured = [
        item for item in featured
        if item.mod.category_id == category.id
    ]

    top = [
        mod for mod in top
        if mod.category_id == category.id
    ]

    new = [
        mod for mod in new
        if mod.category_id == category.id
    ]

    return render_template(
        "browse.html",
        featured=featured,
        top=top,
        ga=ga,
        category=category,
        new=new,
    )


@anonymous.route("/<gameshort>/browse")
def singlegame_browse(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/new")
def singlegame_browse_new_category(
    gameshort: str,
    modcategory: str,
) -> str:
    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    query = request.args.get('query', '')

    mods, page, total_pages = paginate_query(
        apply_search_to_query(
            Mod.query.filter(
                Mod.published.is_(True),
                Mod.game_id == ga.id,
                Mod.category_id == category.id,
            ).order_by(Mod.created.desc()),
            query,
        )
    )

    return render_template(
        "browse-list.html",
        mods=mods,
        sort='new',
        query=query,
        page=page,
        total_pages=total_pages,
        ga=ga,
        category=category,
        url=f"/{gameshort}/{modcategory}/browse/new",
        name=f"Newest {modcategory}s",
        rss=f"/{gameshort}/{modcategory}/browse/new.rss",
    )


@anonymous.route("/<gameshort>/browse/new")
def singlegame_browse_new(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/new",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/new.rss")
def singlegame_browse_new_category_rss(
    gameshort: str,
    modcategory: str,
) -> Response:
    site_name = _cfg('site-name')
    if not site_name:
        abort(404)

    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    mods = Mod.query.filter(
        Mod.published.is_(True),
        Mod.game_id == ga.id,
        Mod.category_id == category.id,
    ).order_by(Mod.created.desc()).limit(30).all()

    return Response(
        render_template(
            "rss.xml",
            mods=mods,
            title=f"New {modcategory}s on {site_name}",
            ga=ga,
            category=category,
            description=f"The newest {modcategory}s on {site_name}",
            url=f"/{gameshort}/{modcategory}/browse/new",
        ),
        mimetype="text/xml",
    )


@anonymous.route("/<gameshort>/browse/new.rss")
def singlegame_browse_new_rss(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/new.rss",
        code=301,
    )

@anonymous.route("/<gameshort>/<modcategory>/browse/updated")
def singlegame_browse_updated_category(
    gameshort: str,
    modcategory: str,
) -> str:
    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    query = request.args.get('query', '')

    mods, page, total_pages = paginate_query(
        apply_search_to_query(
            Mod.query.filter(
                Mod.published.is_(True),
                Mod.game_id == ga.id,
                Mod.category_id == category.id,
                Mod.versions.any(
                    ModVersion.id != Mod.default_version_id
                ),
            ).order_by(Mod.updated.desc()),
            query,
        )
    )

    return render_template(
        "browse-list.html",
        mods=mods,
        sort='updated',
        query=query,
        page=page,
        total_pages=total_pages,
        ga=ga,
        category=category,
        url=f"/{gameshort}/{modcategory}/browse/updated",
        name=f"Recently updated {modcategory}s",
        rss=f"/{gameshort}/{modcategory}/browse/updated.rss",
    )


@anonymous.route("/<gameshort>/browse/updated")
def singlegame_browse_updated(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/updated",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/updated.rss")
def singlegame_browse_updated_category_rss(
    gameshort: str,
    modcategory: str,
) -> Response:
    site_name = _cfg('site-name')

    if not site_name:
        abort(404)

    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    mods = Mod.query.filter(
        Mod.published.is_(True),
        Mod.game_id == ga.id,
        Mod.category_id == category.id,
        Mod.versions.any(
            ModVersion.id != Mod.default_version_id
        ),
    ).order_by(Mod.updated.desc()).limit(30).all()

    return Response(
        render_template(
            "rss.xml",
            mods=mods,
            title=f"Recently updated on {site_name}",
            ga=ga,
            category=category,
            description=f"{modcategory}s on {site_name} updated recently",
            url=f"/{gameshort}/{modcategory}/browse/updated",
        ),
        mimetype="text/xml",
    )


@anonymous.route("/<gameshort>/browse/updated.rss")
def singlegame_browse_updated_rss(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/updated.rss",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/top")
def singlegame_browse_top_category(
    gameshort: str,
    modcategory: str,
) -> str:
    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    query = request.args.get('query', '')

    mods, page, total_pages = paginate_query(
        apply_search_to_query(
            Mod.query.filter(
                Mod.published.is_(True),
                Mod.game_id == ga.id,
                Mod.category_id == category.id,
            ).order_by(Mod.score.desc()),
            query,
        )
    )

    return render_template(
        "browse-list.html",
        mods=mods,
        sort='popularity',
        query=query,
        page=page,
        total_pages=total_pages,
        ga=ga,
        category=category,
        url=f"/{gameshort}/{modcategory}/browse/top",
        name=f"Popular {modcategory}s",
    )


@anonymous.route("/<gameshort>/browse/top")
def singlegame_browse_top(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/top",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/featured")
def singlegame_browse_featured_category(
    gameshort: str,
    modcategory: str,
) -> str:
    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    featured_query = (
        Featured.query
        .join(Featured.mod)
        .filter(
            Mod.game_id == ga.id,
            Mod.category_id == category.id,
            Mod.published.is_(True),
        )
        .order_by(Featured.priority.desc())
    )

    featured, page, total_pages = paginate_query(featured_query)
    mods = [item.mod for item in featured]

    return render_template(
        "browse-list.html",
        mods=mods,
        featured=featured,
        page=page,
        total_pages=total_pages,
        ga=ga,
        category=category,
        url=f"/{gameshort}/{modcategory}/browse/featured",
        name=f"Featured {modcategory}s",
        rss=f"/{gameshort}/{modcategory}/browse/featured.rss",
    )


@anonymous.route("/<gameshort>/browse/featured")
def singlegame_browse_featured(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/featured",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/featured.rss")
def singlegame_browse_featured_category_rss(
    gameshort: str,
    modcategory: str,
) -> Response:
    site_name = _cfg('site-name')

    if not site_name:
        abort(404)

    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    featured = (
        Featured.query
        .join(Featured.mod)
        .filter(
            Mod.game_id == ga.id,
            Mod.category_id == category.id,
            Mod.published.is_(True),
        )
        .order_by(Featured.priority.desc())
        .limit(30)
        .all()
    )

    mods = []

    for featured_mod in featured:
        mod_data = dumb_object(featured_mod.mod)
        mod_data['created'] = (
            featured_mod.created.astimezone(timezone.utc)
        )
        mod_data['game'] = ga
        mod_data['category'] = category
        mods.append(mod_data)

    return Response(
        render_template(
            "rss.xml",
            mods=mods,
            title=f"Featured {modcategory}s on {site_name}",
            ga=ga,
            category=category,
            description=f"Featured {modcategory}s on {site_name}",
            url=f"/{gameshort}/{modcategory}/browse/featured",
        ),
        mimetype="text/xml",
    )


@anonymous.route("/<gameshort>/browse/featured.rss")
def singlegame_browse_featured_rss(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/featured.rss",
        code=301,
    )


@anonymous.route("/<gameshort>/<modcategory>/browse/all")
def singlegame_browse_all_category(
    gameshort: str,
    modcategory: str,
) -> str:
    ga = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if not category:
        abort(404)

    query = request.args.get('query', '')

    mods, page, total_pages = paginate_query(
        apply_search_to_query(
            Mod.query.filter(
                Mod.published.is_(True),
                Mod.game_id == ga.id,
                Mod.category_id == category.id,
            ).order_by(Mod.score.desc()),
            query,
        )
    )

    return render_template(
        "browse-list.html",
        mods=mods,
        sort='popularity',
        query=query,
        page=page,
        total_pages=total_pages,
        ga=ga,
        category=category,
        url=f"/{gameshort}/{modcategory}/browse/all",
        name="All Mods",
    )


@anonymous.route("/<gameshort>/browse/all")
def singlegame_browse_all(
    gameshort: str,
) -> werkzeug.wrappers.Response:
    ga = get_game_info(short=gameshort)

    default_category = next(
        (
            setting.category
            for setting in ga.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if default_category is None:
        abort(
            404,
            description="No default category configured for this game.",
        )

    return redirect(
        f"/{gameshort}/{default_category.stub}/browse/all",
        code=301,
    )


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
    query = request.args.get('query', '')

    mods, page, total_pages = get_paginated_mods(query=query)

    return render_template(
        "browse-list.html",
        mods=mods,
        sort='popularity',
        query=query,
        page=page,
        total_pages=total_pages,
        search=True,
    )


@anonymous.route("/<gameshort>/search")
def singlegame_search(gameshort: str) -> str:
    ga = get_game_info(short=gameshort)
    query = request.args.get('query', '')

    mods, page, total_pages = get_paginated_mods(
        ga,
        query,
    )

    return render_template(
        "browse-list.html",
        mods=mods,
        sort='popularity',
        query=query,
        page=page,
        total_pages=total_pages,
        search=True,
        ga=ga,
    )
