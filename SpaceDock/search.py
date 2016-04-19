from SpaceDock.objects import Mod, ModVersion, User, Game, GameVersion
from SpaceDock.database import db
from SpaceDock.config import _cfg
from sqlalchemy import or_, and_, desc
from flask import session

import math

from datetime import datetime

def weigh_result(result, terms):
    # Factors considered, * indicates important factors:
    # Mods where several search terms match are given a dramatically higher rank*
    # High followers and high downloads get bumped*
    # Mods with a long version history get bumped
    # Mods with lots of screenshots or videos get bumped
    # Mods with a short description get docked
    # Mods lose points the longer they go without updates*
    # Mods get points for supporting the latest KSP version
    # Mods get points for being open source
    # New mods are given a hefty bonus to avoid drowning among established mods
    score = 0
    name_matches = short_matches = 0
    for term in terms:
        if result.name.lower().count(term) != 0:
            name_matches += 1
            score += name_matches * 100
        if result.short_description.lower().count(term) != 0:
            short_matches += 1
            score += short_matches * 50
 
    score *= 100

    score += result.follower_count * 10
    score += result.download_count
    score += len(result.versions) / 5
    score += len(result.media)
    if len(result.description) < 100:
        score -= 10
    if result.updated:
        delta = (datetime.now() - result.updated).days
        if delta > 100:
            delta = 100 # Don't penalize for oldness past a certain point
        score -= delta / 5
    if result.source_link:
        score += 10
    if (result.created - datetime.now()).days < 30:
        score += 100

    return score

def search_mods(ga, text, page, limit):
    terms = text.split(' ')
    query = db.query(Mod).join(Mod.user).join(Mod.versions).join(Mod.game)
    filters = list()
    for term in terms:
        if term.startswith("ver:"):
            filters.append(Mod.versions.any(ModVersion.gameversion.has(GameVersion.friendly_version == term[4:])))
        elif term.startswith("user:"):
            filters.append(User.username == term[5:])
        elif term.startswith("game:"):
            filters.append(Mod.game_id == int(term[5:]))
        elif term.startswith("downloads:>"):
            filters.append(Mod.download_count > int(term[11:]))
        elif term.startswith("downloads:<"):
            filters.append(Mod.download_count < int(term[11:]))
        elif term.startswith("followers:>"):
            filters.append(Mod.follower_count > int(term[11:]))
        elif term.startswith("followers:<"):
            filters.append(Mod.follower_count < int(term[11:]))
        else:
            filters.append(Mod.name.ilike('%' + term + '%'))
            filters.append(User.username.ilike('%' + term + '%'))
            filters.append(Mod.short_description.ilike('%' + term + '%'))
    if ga:
        query = query.filter(Mod.game_id == ga.id)
    query = query.filter(or_(*filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.follower_count)) # We'll do a more sophisticated narrowing down of this in a moment
    total = math.ceil(query.count() / limit)
    if page > total:
        page = total
    if page < 1:
        page = 1
    results = sorted(query.all(), key=lambda r: weigh_result(r, terms), reverse=True)
    return results[(page - 1) * limit:page * limit], total

def search_users(text, page):
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

def typeahead_mods(text):
    query = db.query(Mod)
    filters = list()
    filters.append(Mod.name.ilike('%' + text + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.follower_count)) # We'll do a more sophisticated narrowing down of this in a moment
    results = sorted(query.all(), key=lambda r: weigh_result(r, text.split(' ')), reverse=True)
    return results

def search_users(text, page):
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
