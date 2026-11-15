# SpaceDock API Structure

## Route Migration Table

| Legacy URL | New URL | Method | Function | Request Fields | Legacy Output Fields | New Output Fields | Notes |
|---|---|---|---|---|---|---|---|
| `/api/kspversions` | `/api/game/<ksp_game_id>/version/all` | GET | `kspversions_list` | none | (retired, 501) | version objects (id, friendly_version) | KSP game ID hardcoded in redirect |
| `/api/games` | `/api/game/all` | GET | `games_list` | none | game objects (id, name, short) | game objects (id, name, short) | |
| `/api/publishers` | `/api/publisher/all` | GET | `publishers_list` | none | publisher objects (id, name, type) | publisher objects (id, name, type) | |
| `/api/<gameid>/versions` | `/api/game/<game_id>/version/all` | GET | `gameversions_list` | none | version objects (id, friendly_version) | version objects (id, friendly_version) | |
| `/api/<gameid>/categories` | `/api/game/<game_id>/category/all` | GET | `gamecategories_list` | none | category objects (id, name, stub, sort_order) | category objects (id, name, stub, sort_order) | |
| *none* | `/api/game/<game_id>/category` | POST | `create_category` | name, slug, description | (new) | category object (id, name, slug, sort_order) | |
| *none* | `/api/game/<game_id>/category/<category_id>` | PUT | `update_category` | name, slug, description | (new) | category object (id, name, slug, sort_order) | |
| *none* | `/api/game/<game_id>/category/<category_id>` | DELETE | `delete_category` | none | (new) | none | |
| `/api/<gameid>/notifications` | `/api/game/<game_id>/notification/all` | GET | `game_notifications_list` | none | notification objects (id, name, description, add_url, change_url) | notification objects (id, name, description, add_url, change_url) | |
| `/api/browse` | `/api/game/<game_id>/<category_stub>/browse/all` | GET | `browse` | page, count, sort, order | mod objects (name, id, game, game_id, short_description, downloads, followers, author, default_version_id, shared_authors, background, bg_offset_y, license, website, donations, source_code, url) + versions | mod objects (id, name, description, publisher, downloads, likes, published_at) | |
| `/api/browse/new` | `/api/game/<game_id>/<category_stub>/browse/new` | GET | `browse_new` | page, count | mod objects (same as browse) | mod objects (id, name, description, publisher, published_at) | |
| `/api/browse/top` | `/api/game/<game_id>/<category_stub>/browse/top` | GET | `browse_top` | page, count | mod objects (same as browse) | mod objects (id, name, description, publisher, downloads, likes, score) | |
| `/api/browse/featured` | `/api/game/<game_id>/<category_stub>/browse/featured` | GET | `browse_featured` | page, count | mod objects (same as browse) | mod objects (id, name, description, publisher) | |
| `/api/typeahead/mod` | `/api/game/<game_id>/<category_stub>/search/suggest` | GET | `typeahead_mod` | query | mod objects (id, name) | suggestion objects (id, name) | |
| `/api/search/mod` | `/api/game/<game_id>/<category_stub>/search` | GET | `search_mod` | query, page | mod objects (same as browse) | mod objects (id, name, description, publisher, downloads, likes) | |
| `/api/search/user` | `/api/user/search` | GET | `search_user` | query, page | user objects (id, username) | user objects (id, username) | |
| `/api/login` | `/api/user/login` | POST | `login` | username, password | {error: false} | token object (access_token, expires_in) | |
| `/api/mod/<mod_id>` | `/api/game/<game_id>/<category_stub>/<mod_id>` | GET | `legacy_mod_info_redirect` | none | mod object (name, id, game, game_id, short_description, downloads, followers, author, default_version_id, shared_authors, background, bg_offset_y, license, website, donations, source_code, url) | mod object (id, name, description, game, category, publisher, license, published, ckan, featured, github, downloads, likes, score, locked, default_version, versions, published_at, updated_at) | |
| `/api/mod/<mod_id>/<version>` | `/api/game/<game_id>/<category_stub>/<mod_id>/version/all` | GET | `legacy_mod_version_redirect` | none | version objects (friendly_version, game_version, id, created, download_path, changelog, downloads) | version objects (id, version, download_path, downloads, published_at, dependency) | |
| `/api/ksp-avc/<mod_id>` | `/api/game/<game_id>/<category_stub>/<mod_id>/avc` | GET | `remote_version_file` | none | AVD XML string | AVD XML string | |
| `/api/download_counts` | `/api/game/<game_id>/<category_stub>/download/stat` | POST | `download_counts` | mod_ids (array) | download stats objects (id, count) | download stat objects (mod_id, count) | |
| `/api/user/<username>` | `/api/user/<username>` | GET | `user_info_api` | none | user object (username, description, forumUsername, ircNick, twitterUsername, redditUsername) | user object (id, username, avatar, bio, email, public, mods_count) | |
| `/api/user/<username>/change-password` | `/api/user/<username>/password` | POST | `change_password` | password, confirm_password | {error: false} or {error: true, reason} | none | |
| `/api/user/<username>/delete` | `/api/user/<username>` | DELETE | `delete_user` | none | {error: false} | none | |
| `/api/mod/<mod_id>/update-bg` | `/api/game/<game_id>/<category_stub>/<mod_id>/background` | POST | `legacy_update_mod_bg_redirect` | image (file) | {path: null} or {path: url} | mod object (id, name, background) | |
| `/api/user/<username>/update-bg` | `/api/user/<username>/background` | POST | `update_user_background` | image (file) | {path: null} or {path: url} | user object (id, username, background) | |
| `/api/pack/<pack_id>/update-bg` | `/api/game/<game_id>/pack/<pack_id>/background` | POST | `update_pack_background` | image (file) | {path: null} or {path: url} | pack object (id, name, background) | |
| `/api/<game_id>/update-bg` | `/api/game/<game_id>/background` | POST | `update_game_background` | image (file) | {path: null} or {path: url} | game object (id, name, background) | |
| `/api/mod/<mod_id>/grant` | `/api/game/<game_id>/<category_stub>/<mod_id>/grant` | POST | `legacy_grant_redirect` | username | {error: false} | grant object (id, username) | |
| `/api/mod/<mod_id>/accept_grant` | `/api/game/<game_id>/<category_stub>/<mod_id>/grant/accept` | POST | `legacy_accept_grant_redirect` | none | {error: false} | mod object (id, name, publisher) | |
| `/api/mod/<mod_id>/reject_grant` | `/api/game/<game_id>/<category_stub>/<mod_id>/grant/reject` | POST | `legacy_reject_grant_redirect` | none | {error: false} | mod object (id, name, publisher) | |
| `/api/mod/<mod_id>/revoke` | `/api/game/<game_id>/<category_stub>/<mod_id>/revoke` | POST | `legacy_revoke_redirect` | username | {error: false} | mod object (id, name, publisher) | |
| `/api/mod/<mod_id>/set-default/<vid>` | `/api/game/<game_id>/<category_stub>/<mod_id>/version/<vid>/default` | POST | `legacy_set_default_redirect` | none | {error: false} | mod object (id, name, default_version) | |
| `/api/pack/create` | `/api/game/<game_id>/pack` | POST | `create_list` | name, description | {url: url} | pack object (id, name, description, mods_count) | |
| `/api/mod/create` | `/api/game/<game_id>/<category_stub>` | POST | `legacy_mod_create_redirect` | name, game_id, category | {url: url} | mod object (id, name, publisher) | |
| `/api/mod/<mod_id>/update` | `/api/game/<game_id>/<category_stub>/<mod_id>` | PUT | `legacy_mod_update_redirect` | mod fields | {} | mod object (id, name, description, publisher, category) | |
| `/api/mod/<mod_id>/edit_version` | `/api/game/<game_id>/<category_stub>/<mod_id>/version/<version>` | PUT | `legacy_edit_version_redirect` | version fields | {url: url} | version object (id, version, download_path, downloads) | |
| *none* | `/api/publisher/<publisher_id>` | GET | `publisher_info` | none | (new) | publisher object (id, name, type, avatar, bio, mods_count) | |
| *none* | `/api/publisher/<publisher_id>` | PUT | `publisher_update` | name, type, avatar, bio | (new) | publisher object (id, name, type, avatar, bio) | |
| *none* | `/api/publisher/<publisher_id>` | DELETE | `publisher_delete` | none | (new) | none | |
| *none* | `/api/game/<game_id>` | GET | `game_info` | none | (new) | game object (id, name, short, active, versions_count, mods_count) | |
| *none* | `/api/game/<game_id>/<category_stub>/<mod_id>/version/<vid>` | GET | `version_info` | none | (new) | version object (id, version, download_path, downloads, published_at, dependency) | |
| *none* | `/api/game/<game_id>/<category_stub>/<mod_id>/download/stat` | GET | `single_mod_download_stats` | none | (new) | download stat object (mod_id, count) | |
| *none* | `/api/game/<game_id>/<category_stub>/<mod_id>` | DELETE | `delete_creation` | none | (new) | none | |
| *none* | `/api/game/<game_id>/pack/<pack_id>` | PUT | `update_pack` | name, description | (new) | pack object (id, name, description, mods_count) | |
| *none* | `/api/game/<game_id>/pack/<pack_id>` | DELETE | `delete_pack` | none | (new) | none | |
| *none* | `/api/game/<game_id>/<category_stub>/browse/extended` | GET | `browse_extended` | tags, published, min_downloads, created_after | (new) | mod objects (id, name, description, publisher, downloads, likes) | |
| *none* | `/api/game/<game_id>/<category_stub>/search/extended` | GET | `search_extended` | sort, order, tags, published | (new) | mod objects (id, name, description, publisher) | |
| *none* | `/api/game/<game_id>/<category_stub>/<mod_id>/media` | GET | `creation_media` | none | (new) | media objects (id, url, type) | |
| *none* | `/api/game/<game_id>/<category_stub>/<mod_id>/media` | POST | `add_media` | image (file) | (new) | media object (id, url, type) | |

## Field Mapping Notes

### Mod Info (legacy → new)
- `author` → `publisher` (object with id, name)
- `game` → `game` (object with id, name)
- `game_id` → `game.id`
- `short_description` → `description`
- `downloads` → `downloads`
- `followers` → `likes`
- `default_version_id` → `default_version` (object)
- `shared_authors` → (removed)
- `background` → `background`
- `bg_offset_y` → (removed)
- `license` → `license`
- `website` → (removed)
- `donations` → (removed)
- `source_code` → (removed)
- `url` → (removed)

### Version Info (legacy → new)
- `friendly_version` → `version`
- `game_version` → (removed)
- `id` → `id`
- `created` → `published_at`
- `download_path` → `download_path`
- `changelog` → (removed)
- `downloads` → `downloads`

### User Info (legacy → new)
- `username` → `username`
- `description` → `bio`
- `forumUsername` → (removed)
- `ircNick` → (removed)
- `twitterUsername` → (removed)
- `redditUsername` → (removed)

## Routes Marked for Removal
Routes without legacy URLs that require new database models not yet created:
- Tag routes (no Tag model)
- Like routes (no Like model, only `likes_count` counter on Mod)
- Comment routes (no Comment model)
- User notification routes (no UserNotification model; existing Notification is game webhook definition)