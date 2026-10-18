
import json
import re
from typing import Tuple, List, Union, Optional

import werkzeug.wrappers
from flask import (
    Blueprint,
    render_template,
    url_for,
    abort,
    redirect,
    request,
)
from flask_login import current_user
from sqlalchemy import or_

from ..config import _cfg
from ..common import (
    loginrequired,
    with_session,
    get_game_info,
    paginate_query,
    sendfile,
)
from ..database import db
from ..objects import Mod, ModList, ModListItem, Game, ModCategory

lists = Blueprint("lists", __name__)


def _get_mod_list(list_id: str) -> Tuple[ModList, Game, bool]:
    mod_list = ModList.query.get(list_id)

    if not mod_list:
        abort(404)

    game = Game.query.get(mod_list.game_id)

    if not game:
        abort(404)

    editable = False

    if current_user.is_authenticated:
        if current_user.admin or current_user.id == mod_list.user_id:
            editable = True

    return mod_list, game, editable


def _default_pack_category(game: Game) -> ModCategory:
    category = next(
        (
            setting.category
            for setting in game.mod_category_settings
            if setting.enabled
            and setting.default
            and setting.category is not None
        ),
        None,
    )

    if category is None:
        abort(
            404,
            description="No default mod category configured for this game",
        )

    return category


def canonical_pack_url(mod_list: ModList) -> str:
    game = Game.query.get(mod_list.game_id)

    if game is None:
        abort(404)

    category = _default_pack_category(game)

    return url_for(
        "lists.view_list",
        gameshort=game.short,
        modcategory=category.stub,
        list_id=mod_list.id,
        list_name=mod_list.name,
    )


def _canonical_pack_action_url(
    endpoint: str,
    mod_list: ModList,
    **extra,
) -> str:
    game = Game.query.get(mod_list.game_id)

    if game is None:
        abort(404)

    category = _default_pack_category(game)

    values = {
        "gameshort": game.short,
        "modcategory": category.stub,
        "list_id": mod_list.id,
        "list_name": mod_list.name,
    }
    values.update(extra)

    return url_for(endpoint, **values)


def _legacy_pack_redirect(
    list_id: str,
    old_path: str = "",
) -> werkzeug.wrappers.Response:
    mod_list, game, editable = _get_mod_list(list_id)

    target = canonical_pack_url(mod_list).rstrip("/")
    remainder = old_path

    # Remove the old pack name from the remaining path.
    if mod_list.name and remainder:
        remainder = re.sub(
            rf"^{re.escape(mod_list.name.strip('/'))}(?=/|$)",
            "",
            remainder,
            count=1,
        )

    if remainder:
        target += "/" + remainder.lstrip("/")

    # Preserve query parameters.
    if request.query_string:
        target += "?" + request.query_string.decode("latin-1")

    return redirect(target, code=301)


@lists.route("/packs", defaults={"gameshort": None})
@lists.route("/packs/<gameshort>")
def packs(
    gameshort: Optional[str],
) -> Union[str, werkzeug.wrappers.Response]:
    if not gameshort:
        query = (
            ModList.query
            .filter(ModList.mods.any())
            .order_by(ModList.created.desc())
        )

        packs, page, total_pages = paginate_query(query, 9)

        return render_template(
            "packs.html",
            ga=None,
            game=None,
            category=None,
            packs=packs,
            page=page,
            total_pages=total_pages,
        )

    game = get_game_info(short=gameshort)
    category = _default_pack_category(game)

    return redirect(
        url_for(
            "lists.packs_by_category",
            gameshort=game.short,
            modcategory=category.stub,
        ),
        code=301,
    )


@lists.route("/<gameshort>/<modcategory>/packs")
def packs_by_category(gameshort: str, modcategory: str) -> str:
    game = get_game_info(short=gameshort)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if category is None:
        abort(404)

    if not any(
        setting.enabled
        and setting.category_id == category.id
        for setting in game.mod_category_settings
    ):
        abort(404)

    query = (
        ModList.query
        .filter(ModList.mods.any())
        .filter(ModList.game_id == game.id)
        .order_by(ModList.created.desc())
    )

    packs, page, total_pages = paginate_query(query, 9)

    return render_template(
        "packs.html",
        ga=game,
        game=game,
        category=category,
        packs=packs,
        page=page,
        total_pages=total_pages,
    )


@lists.route("/create/pack")
def create_list() -> str:
    games = (
        Game.query
        .filter(Game.active == True)
        .order_by(Game.id.desc())
        .all()
    )
    game = Game.query.order_by(Game.id.desc()).first()

    return render_template(
        "create_list.html",
        games=games,
        ga=game,
    )


# Legacy pack URLs.
# Keep these routes for old bookmarks and links.
@lists.route("/pack/<int:list_id>", defaults={"old_path": ""})
@lists.route("/pack/<int:list_id>/<path:old_path>")
def legacy_pack_url(
    list_id: int,
    old_path: str,
) -> werkzeug.wrappers.Response:
    return _legacy_pack_redirect(str(list_id), old_path)


# Canonical pack view URL.
@lists.route(
    "/<gameshort>/<modcategory>/pack/<int:list_id>/<path:list_name>"
)
def view_list(
    gameshort: str,
    modcategory: str,
    list_id: int,
    list_name: str,
) -> str:
    mod_list, game, editable = _get_mod_list(str(list_id))

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if category is None:
        abort(404)

    if game.short != gameshort:
        abort(404)

    if not any(
        setting.enabled
        and setting.category_id == category.id
        for setting in game.mod_category_settings
    ):
        abort(404)

    # Redirect incorrect names or categories to the canonical URL.
    canonical = canonical_pack_url(mod_list)

    if request.path != canonical:
        return redirect(canonical, code=301)

    return render_template(
        "mod_list.html",
        mod_list=mod_list,
        background=mod_list.background_url(
            _cfg("protocol"),
            _cfg("cdn-domain"),
        ),
        editable=editable,
        ga=game,
        category=category,
    )


# Canonical pack edit URL.
@lists.route(
    "/<gameshort>/<modcategory>/pack/<int:list_id>/<path:list_name>/edit",
    methods=["GET", "POST"],
)
@with_session
@loginrequired
def edit_list(
    gameshort: str,
    modcategory: str,
    list_id: int,
    list_name: str,
) -> Union[str, werkzeug.wrappers.Response]:
    mod_list, game, editable = _get_mod_list(str(list_id))

    if not editable:
        abort(403)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if category is None:
        abort(404)

    if game.short != gameshort:
        abort(404)

    if not any(
        setting.enabled
        and setting.category_id == category.id
        for setting in game.mod_category_settings
    ):
        abort(404)

    if request.method == "GET":
        canonical = _canonical_pack_action_url(
            "lists.edit_list",
            mod_list,
        )

        # The canonical view URL has an /edit suffix.
        canonical += "/edit"

        if request.path != canonical:
            return redirect(canonical, code=301)

        return render_template(
            "edit_list.html",
            mod_list=mod_list,
            background=mod_list.background_url(
                _cfg("protocol"),
                _cfg("cdn-domain"),
            ),
            mod_ids=[item.mod.id for item in mod_list.mods],
            ga=game,
            category=category,
        )

    name = request.form.get("name", "")
    description = request.form.get("description")
    bg_offset_y = request.form.get("bg-offset-y", 0)

    try:
        mods = json.loads(request.form.get("mods", ""))
    except (TypeError, ValueError):
        abort(400)

    if not isinstance(mods, list):
        abort(400)

    if not name or len(name) > 100:
        abort(400)

    # Validate every submitted mod ID and ensure it belongs to this game.
    selected_mods = []

    for mod_id in mods:
        mod = Mod.query.get(mod_id)

        if mod is None or mod.game_id != mod_list.game_id:
            abort(400)

        selected_mods.append(mod)

    mod_list.name = name
    mod_list.description = description

    # The background path is updated by /api/pack/<id>/update-bg.
    try:
        mod_list.bgOffsetY = int(bg_offset_y)
    except (TypeError, ValueError):
        pass

    selected_ids = [mod.id for mod in selected_mods]

    # Remove mods no longer in the pack.
    removed_mods = [
        item
        for item in mod_list.mods
        if item.mod_id not in selected_ids
    ]

    for item in removed_mods:
        mod_list.mods.remove(item)
        db.delete(item)

    # Add new mods.
    existing_ids = {
        item.mod_id
        for item in mod_list.mods
    }

    for mod in selected_mods:
        if mod.id not in existing_ids:
            item = ModListItem()
            item.mod_id = mod.id
            item.mod_list = mod_list
            db.add(item)
            mod_list.mods.append(item)

    # Keep the requested order.
    items_by_mod_id = {
        item.mod_id: item
        for item in mod_list.mods
    }

    for index, mod_id in enumerate(selected_ids):
        item = items_by_mod_id.get(mod_id)

        if item is not None:
            item.sort_index = index

    db.commit()

    return redirect(canonical_pack_url(mod_list))


# Canonical pack deletion URL.
@lists.route(
    "/<gameshort>/<modcategory>/pack/<int:list_id>/delete",
    methods=["GET", "POST"],
)
@loginrequired
@with_session
def delete(
    gameshort: str,
    modcategory: str,
    list_id: int,
) -> werkzeug.wrappers.Response:
    mod_list, game, editable = _get_mod_list(str(list_id))

    if not editable:
        abort(403)

    category = ModCategory.query.filter_by(
        stub=modcategory
    ).first()

    if category is None:
        abort(404)

    if game.short != gameshort:
        abort(404)

    if not any(
        setting.enabled
        and setting.category_id == category.id
        for setting in game.mod_category_settings
    ):
        abort(404)

    db.delete(mod_list)
    db.commit()

    return redirect("/profile/" + current_user.username)


@lists.route(
    "/<gameshort>/<modcategory>/pack/<int:pack_id>/<path:pack_name>/background"
)
def list_background(
    gameshort: str,
    modcategory: str,
    pack_id: int,
    pack_name: str,
) -> werkzeug.wrappers.Response:
    pack = ModList.query.get(pack_id)

    if pack is None:
        abort(404)

    if not pack.background:
        abort(404)

    return sendfile(pack.background, False)


@lists.route(
    "/<gameshort>/<modcategory>/pack/<int:pack_id>/<path:pack_name>/thumb"
)
def list_thumbnail(
    gameshort: str,
    modcategory: str,
    pack_id: int,
    pack_name: str,
) -> werkzeug.wrappers.Response:
    pack = ModList.query.get(pack_id)

    if pack is None:
        abort(404)

    if not pack.thumbnail:
        abort(404)

    return sendfile(pack.thumbnail, False)
