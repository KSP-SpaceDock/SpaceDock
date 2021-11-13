import math
import re
from datetime import datetime
from typing import List, Iterable, Tuple, Optional

from packaging import version
from sqlalchemy import and_, or_, not_, desc
from sqlalchemy.orm import Query

from .database import db
from .objects import Mod, ModVersion, User, Game, GameVersion


def get_mod_score(mod: Mod) -> int:
    # Factors considered, * indicates important factors:
    # High followers and high downloads get bumped*
    # Mods that other users include in their mod packs get bumped
    # Mods with a long version history get bumped
    # Mods with lots of screenshots or videos get bumped
    # Mods with a short description get docked
    # Mods lose points the longer they go without updates*
    # Mods get points for supporting the latest KSP version
    # Mods get points for being open source
    # New mods are given a hefty bonus to avoid drowning among established mods
    score = 0
    if mod.default_version is None:
        return score
    score += mod.download_count
    score += 10 * mod.follower_count
    score += 15 * len({itm.mod_list for itm in mod.mod_list_items if itm.mod_list.user_id != mod.user_id})
    score += len(mod.versions) // 5
    score += len(mod.media)
    if len(mod.description) < 100:
        score -= 10
    if mod.updated:
        delta = (datetime.now() - mod.updated).days
        if delta > 100:
            delta = 100  # Don't penalize for oldness past a certain point
        score -= delta / 5
    if mod.source_link:
        score += 10
    if (mod.created - datetime.now()).days < 30:
        score += 100
    # 5% penalty for each game version newer than the latest compatible (capped at 90%)
    num_incompat = versions_behind(mod)
    if num_incompat > 0:
        penalty = min(0.05 * num_incompat, 0.9)
        score = int(score * (1.0 - penalty))
    return score


def versions_behind(mod: Mod) -> int:
    try:
        all = game_versions(mod.game)
        compat = version.Version(mod.default_version.gameversion.friendly_version)
        return sum(1 for v in all if v > compat)
    except version.InvalidVersion:
        return 0


def game_versions(game: Game) -> Iterable[version.Version]:
    for gv in game.versions:
        try:
            ver = version.Version(gv.friendly_version)
            yield ver
        except version.InvalidVersion:
            pass


# Optional '-' at start, followed by:
#   1. "term with spaces", OR
#   2. termwithoutquotesorspaces
SEARCH_TOKEN_PATTERN = re.compile(r'-?(?:"[^"]*"|[^" ]+)')


def search_mods(game_id: Optional[int], text: str, page: int, limit: int) -> Tuple[List[Mod], int]:
    terms = [term.replace('"', '') for term in SEARCH_TOKEN_PATTERN.findall(text)]
    query = db.query(Mod).join(Mod.user).join(Mod.game)
    if game_id:
        query = query.filter(Mod.game_id == game_id)
    query = query.filter(Mod.published)

    # All of the terms must match
    query = query.filter(*(term_to_filter(term) for term in terms))

    query = query.order_by(desc(Mod.score))

    total_pages = math.ceil(query.count() / limit)
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1
    mods = query.offset(limit * (page - 1)).limit(limit).all()

    return mods, total_pages


def term_to_filter(term: str) -> Query:
    if term.startswith('-'):
        return not_(term_to_filter(term[1:]))
    elif term.startswith("ver:"):
        return Mod.versions.any(ModVersion.gameversion.has(or_(
            GameVersion.friendly_version == term[4:],
            GameVersion.friendly_version.ilike(f'{term[4:]}.%'))))
    elif term.startswith("user:"):
        return User.username == term[5:]
    elif term.startswith("game:"):
        to_match = term[5:]
        return (Mod.game_id == int(to_match)
                if to_match.isnumeric() else
                Game.name.ilike(f'%{to_match}%'))
    elif term.startswith("downloads:>"):
        return Mod.download_count > int(term[11:])
    elif term.startswith("downloads:<"):
        return Mod.download_count < int(term[11:])
    elif term.startswith("followers:>"):
        return Mod.follower_count > int(term[11:])
    elif term.startswith("followers:<"):
        return Mod.follower_count < int(term[11:])
    else:
        # Now the leftover is probably what the user thinks the mod name is.
        # ALL of them have to match again, however we don't care if it's in the name or description.
        return or_(Mod.name.ilike('%' + term + '%'),
                   Mod.short_description.ilike('%' + term + '%'),
                   Mod.description.ilike('%' + term + '%'))


def search_users(text: str, page: int) -> Iterable[User]:
    terms = text.split(' ')
    query = db.query(User)
    filters = list()
    for term in terms:
        filters.append(User.username.ilike('%' + term + '%'))
        filters.append(User.description.ilike('%' + term + '%'))
        filters.append(User.forumUsername.ilike('%' + term + '%'))
        filters.append(User.ircNick.ilike('%' + term + '%'))
        filters.append(User.twitterUsername.ilike('%' + term + '%'))
        filters.append(User.redditUsername.ilike('%' + term + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(User.public == True)
    query = query.order_by(User.username)
    query = query.limit(100)
    results = query.all()
    return results[page * 10:page * 10 + 10]


def typeahead_mods(game_id: str, text: str) -> Iterable[Mod]:
    query = db.query(Mod)
    filters = list()
    filters.append(Mod.name.ilike('%' + text + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(Mod.game_id == game_id, Mod.published == True)
    query = query.order_by(desc(Mod.score))
    results = query.all()
    return results
