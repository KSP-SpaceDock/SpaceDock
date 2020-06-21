import math
from datetime import datetime
from typing import List, Iterable, Tuple, Optional, Union

from sqlalchemy import and_, or_, desc

from .database import db
from .objects import Mod, ModVersion, User, Game, GameVersion


def get_mod_score(mod: Mod) -> int:
    # Factors considered, * indicates important factors:
    # High followers and high downloads get bumped*
    # Mods with a long version history get bumped
    # Mods with lots of screenshots or videos get bumped
    # Mods with a short description get docked
    # Mods lose points the longer they go without updates*
    # Mods get points for supporting the latest KSP version
    # Mods get points for being open source
    # New mods are given a hefty bonus to avoid drowning among established mods
    score = 0
    score += mod.follower_count * 10
    score += mod.download_count
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
    return score


def search_mods(ga: Optional[Game], text: str, page: int, limit: int) -> Tuple[List[Mod], int]:
    terms = text.split(' ')
    query = db.query(Mod).join(Mod.user).join(Mod.versions).join(Mod.game)
    and_filters = list()
    or_filters = list()
    for term in terms:
        if term.startswith("ver:"):
            and_filters.append(Mod.versions.any(ModVersion.gameversion.has(
                GameVersion.friendly_version == term[4:])))
        elif term.startswith("user:"):
            and_filters.append(User.username == term[5:])
        elif term.startswith("game:"):
            and_filters.append(Mod.game_id == int(term[5:]))
        elif term.startswith("downloads:>"):
            and_filters.append(Mod.download_count > int(term[11:]))
        elif term.startswith("downloads:<"):
            and_filters.append(Mod.download_count < int(term[11:]))
        elif term.startswith("followers:>"):
            and_filters.append(Mod.follower_count > int(term[11:]))
        elif term.startswith("followers:<"):
            and_filters.append(Mod.follower_count < int(term[11:]))
        else:
            or_filters.append(Mod.name.ilike('%' + term + '%'))
            or_filters.append(User.username.ilike('%' + term + '%'))
            or_filters.append(Mod.short_description.ilike('%' + term + '%'))
    if ga:
        query = query.filter(Mod.game_id == ga.id)
    query = query.filter(and_(*and_filters))
    query = query.filter(or_(*or_filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.score))

    total_pages = math.ceil(query.count() / limit)
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1
    mods = query.offset(limit * (page - 1)).limit(limit).all()

    return mods, total_pages


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


def typeahead_mods(text: str) -> Iterable[Mod]:
    query = db.query(Mod)
    filters = list()
    filters.append(Mod.name.ilike('%' + text + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.score))
    results = query.all()
    return results
