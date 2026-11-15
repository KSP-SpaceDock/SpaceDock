# SpaceDock API v2

Base URL: `https://spacedock.info/api`

All endpoints return JSON. Use `Accept: application/json` header.

## Authentication

Most endpoints require authentication via session cookies.

```http
# Session-based auth (browser)
Cookie: session=<session_id>
```

## Games

### List All Games

```http
GET /api/game/all
```

Returns list of all supported games with their IDs.

**Response:** Array of game objects
```json
[
  {
    "id": 1,
    "name": "Kerbal Space Program",
    "short": "ksp",
    "active": true
  }
]
```

### Get Game Info

```http
GET /api/game/<game_id>
```

**Response:**
```json
{
  "id": 1,
  "name": "Kerbal Space Program",
  "short": "ksp",
  "active": true,
  "versions_count": 10,
  "mods_count": 1000
}
```

### List Game Versions

```http
GET /api/game/<game_id>/version/all
```

**Response:** Array of version objects
```json
[
  {
    "id": 1,
    "friendly_version": "1.12.4"
  }
]
```

### Update Game Background

```http
POST /api/game/<game_id>/background
```

Update the background image for a game. Requires admin.

## Categories

### List Game Categories

```http
GET /api/game/<game_id>/category/all
```

**Response:** Array of category objects
```json
[
  {
    "id": 1,
    "name": "Mods",
    "stub": "mods",
    "sort_order": 1
  }
]
```

### Create Category

```http
POST /api/game/<game_id>/category
```

Create a new mod category. Requires admin.

**Parameters:**
- `name`: Category name
- `slug`: URL slug
- `description` (optional): Category description

### Update Category

```http
PUT /api/game/<game_id>/category/<category_id>
```

Update an existing category. Requires admin.

### Delete Category

```http
DELETE /api/game/<game_id>/category/<category_id>
```

Delete a category. Requires admin.

## Browse

### Browse All Mods

```http
GET /api/game/<game_id>/<category_stub>/browse/all
```

List all mods in a category with pagination.

**Parameters:**
- `page` (optional): Page number (default: 1)
- `count` (optional): Items per page (default: 30)
- `sort` (optional): Sort field (`downloads` or `name`)
- `order` (optional): Sort order (`asc` or `desc`)

**Response:**
```json
{
  "total": 1000,
  "count": 30,
  "pages": 34,
  "page": 1,
  "result": [
    {
      "id": 1,
      "name": "Example Mod",
      "description": "Short description",
      "game": { "id": 1, "name": "KSP" },
      "publisher": "author",
      "downloads": 100,
      "likes": 10
    }
  ]
}
```

### Browse New Mods

```http
GET /api/game/<game_id>/<category_stub>/browse/new
```

List recently added mods. Parameters: `page`, `count`.

### Browse Top Mods

```http
GET /api/game/<game_id>/<category_stub>/browse/top
```

List most popular mods. Parameters: `page`, `count`.

### Browse Featured Mods

```http
GET /api/game/<game_id>/<category_stub>/browse/featured
```

List featured mods. Parameters: `page`, `count`.

### Browse Extended

```http
GET /api/game/<game_id>/<category_stub>/browse/extended
```

Browse mods with extended filtering options.

**Parameters:**
- `published` (optional): Filter by publication status (`true` or `false`)
- `min_downloads` (optional): Minimum download count
- `created_after` (optional): ISO 8601 date to filter mods created after

## Search

### Search Mods

```http
GET /api/game/<game_id>/<category_stub>/search
```

Search mods by query string.

**Parameters:**
- `query`: Search query
- `page` (optional): Page number

### Search Extended

```http
GET /api/game/<game_id>/<category_stub>/search/extended
```

Search mods with extended filtering and sorting.

**Parameters:**
- `query`: Search query
- `sort` (optional): Sort by `downloads` or `name`
- `order` (optional): Sort order `asc` or `desc`
- `published` (optional): Filter by publication status

### Search Users

```http
GET /api/user/search
```

Search users by username.

**Parameters:**
- `query`: Search query
- `page` (optional): Page number

### Typeahead Search

```http
GET /api/game/<game_id>/<category_stub>/search/suggest
```

Autocomplete suggestions for mod search.

**Parameters:**
- `query`: Partial search term

## Mod Management

### Create Mod

```http
POST /api/game/<game_id>/<category_stub>
```

Create a new mod.

**Parameters:**
- `name`: Mod name
- `description` (optional): Mod description

### Get Mod Info

```http
GET /api/game/<game_id>/<category_stub>/<mod_id>
```

Get detailed information about a mod.

**Response:**
```json
{
  "id": 1,
  "name": "Example Mod",
  "description": "Short description",
  "game": { "id": 1, "name": "KSP" },
  "publisher": "author",
  "downloads": 100,
  "likes": 10,
  "published_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-02T00:00:00",
  "default_version": "1.0.0",
  // Legacy-compatible fields
  "author": "author",
  "game_id": 1,
  "short_description": "Short description",
  "followers": 10,
  "default_version_id": 1,
  "shared_authors": [],
  "background": "https://...",
  "bg_offset_y": 0,
  "license": "MIT",
  "website": "https://...",
  "donations": "https://...",
  "source_code": "https://github.com/...",
  "url": "/game/1/mods/1/example-mod"
}
```

### Update Mod

```http
PUT /api/game/<game_id>/<category_stub>/<mod_id>
```

Update an existing mod.

### Delete Mod

```http
DELETE /api/game/<game_id>/<category_stub>/<mod_id>
```

Delete a mod.

### Update Mod Background

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/background
```

Update the background image for a mod.

### Mod Media

```http
GET /api/game/<game_id>/<category_stub>/<mod_id>/media
```

List media files for a mod.

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/media
```

Add media file to a mod.

```http
DELETE /api/game/<game_id>/<category_stub>/<mod_id>/media/<media_id>
```

Remove media file from a mod.

### AVC Version File

```http
GET /api/game/<game_id>/<category_stub>/<mod_id>/avc
```

Get Remote Version File in AVC format for version checking.

## Versions

### List Versions

```http
GET /api/game/<game_id>/<category_stub>/<mod_id>/version/all
```

List all versions of a mod.

**Response:** Array of version objects
```json
[
  {
    "id": 1,
    "version": "1.0.0",
    "download_path": "/download/...",
    "downloads": 50,
    "published_at": "2026-01-01T00:00:00"
  }
]
```

### Get Version Info

```http
GET /api/game/<game_id>/<category_stub>/<mod_id>/version/<vid>
```

Get information about a specific version.

### Update Version

```http
PUT /api/game/<game_id>/<category_stub>/<mod_id>/version/<vid>
```

Update a version.

### Set Default Version

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/version/<vid>/default
```

Set a version as the default version.

## Downloads

### Download Statistics

```http
POST /api/game/<game_id>/<category_stub>/download/stat
```

Report download statistics for multiple mods.

### Single Mod Download Stats

```http
GET /api/game/<game_id>/<category_stub>/<mod_id>/download/stat
```

Get download count for a single mod.

### Bulk Download Counts

```http
POST /api/download_counts
```

Get download counts for multiple mods.

## Author Management

### Grant Shared Author

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/grant
```

Grant shared author permission.

**Parameters:**
- `username`: Username to grant to

### Accept Grant

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/grant/accept
```

Accept a shared author grant.

### Reject Grant

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/grant/reject
```

Reject a shared author grant.

### Revoke Shared Author

```http
POST /api/game/<game_id>/<category_stub>/<mod_id>/revoke
```

Revoke shared author permission.

## Pack Management

### Create Pack

```http
POST /api/game/<game_id>/pack
```

Create a new mod pack.

**Parameters:**
- `name`: Pack name
- `description` (optional): Pack description

### Update Pack

```http
PUT /api/game/<game_id>/pack/<pack_id>
```

Update an existing pack.

### Delete Pack

```http
DELETE /api/game/<game_id>/pack/<pack_id>
```

Delete a pack.

### Update Pack Background

```http
POST /api/game/<game_id>/pack/<pack_id>/background
```

Update pack background image.

## Publishers

### List Publishers

```http
GET /api/publisher/all
```

List all publishers.

### Get Publisher Info

```http
GET /api/publisher/<publisher_id>
```

Get publisher information.

**Response:**
```json
{
  "id": 1,
  "name": "Publisher Name",
  "type": "user",
  "avatar": "https://...",
  "bio": "Publisher bio",
  "mods_count": 10
}
```

## Users

### Get User Info

```http
GET /api/user/<username>
```

Get user profile information.

**Response:**
```json
{
  "id": 1,
  "username": "user1",
  "avatar": "https://...",
  "bio": "User bio",
  "mods_count": 5
}
```

### Delete User

```http
DELETE /api/user/<username>
```

Delete a user. Requires admin or self.

### Change Password

```http
POST /api/user/<username>/password
```

Change user password.

**Parameters:**
- `password`: New password
- `confirm_password`: Confirm new password

### Update User Background

```http
POST /api/user/<username>/background
```

Update user profile background.

### List User Creations

```http
GET /api/user/<username>/creation/all
```

List all mods created by a user.

**Parameters:**
- `published` (optional): Filter by publication status (`true` or `false`)

**Response:**
```json
{
  "page": 1,
  "pages": 1,
  "mods": [...]
}
```

### List User Packs

```http
GET /api/user/<username>/pack/all
```

List all packs created by a user.

**Response:**
```json
{
  "page": 1,
  "pages": 1,
  "packs": [
    {
      "id": 1,
      "name": "My Pack",
      "description": "Pack description",
      "game": "KSP",
      "game_id": 1,
      "author": "user1",
      "created": "2026-01-01T00:00:00"
    }
  ]
}
```

## Notifications

### List Game Notifications

```http
GET /api/game/<game_id>/notification/all
```

List notifications for a game.

## Legacy Routes

These routes are maintained for backward compatibility. They return the same response format as new routes.

### Games

```http
GET /api/games          → /api/game/all
GET /api/kspversions    → /api/game/1/version/all
```

### Mods

```http
GET /api/mod/<id>               → /api/game/<game_id>/<category>/<id>
GET /api/mod/<id>/<version>     → /api/game/<game_id>/<category>/<id>/version/<vid>
GET /api/ksp-avc/<id>           → /api/game/1/<category>/<id>/avc
POST /api/mod/create            → /api/game/<game_id>/<category>
PUT /api/mod/<id>/update        → /api/game/<game_id>/<category>/<id>
PUT /api/mod/<id>/update-bg     → /api/game/<game_id>/<category>/<id>/background
PUT /api/mod/<id>/edit_version  → /api/game/<game_id>/<category>/<id>/version/<vid>
```

### Grants

```http
POST /api/mod/<id>/grant      → /api/game/<game_id>/<category>/<id>/grant
POST /api/mod/<id>/accept_grant  → /api/game/<game_id>/<category>/<id>/grant/accept
POST /api/mod/<id>/reject_grant  → /api/game/<game_id>/<category>/<id>/grant/reject
POST /api/mod/<id>/revoke      → /api/game/<game_id>/<category>/<id>/revoke
```

### Versions

```http
POST /api/mod/<id>/set-default/<vid> → /api/game/<game_id>/<category>/<id>/version/<vid>/default
```

### Packs

```http
POST /api/pack/create       → /api/game/<game_id>/pack
POST /api/pack/<id>/update-bg → /api/game/<game_id>/pack/<id>/background
```

### Browse

```http
GET /api/browse              → /api/game/<game_id>/<category>/browse/all
GET /api/browse/new          → /api/game/<game_id>/<category>/browse/new
GET /api/browse/top          → /api/game/<game_id>/<category>/browse/top
GET /api/browse/featured     → /api/game/<game_id>/<category>/browse/featured
```

### Search

```http
GET /api/search/mod          → /api/game/<game_id>/<category>/search
GET /api/typeahead/mod       → /api/game/<game_id>/<category>/search/suggest
```

### Downloads

```http
POST /api/download_counts    → /api/game/<game_id>/<category>/download/stat
```