SpaceDock API Documentation
Overview

This document describes the REST API routes implemented in api.py.

Base URL

All endpoints are relative to the application root.

https://your-domain.com

Response format

Most endpoints return JSON. The @json_output decorator handles response serialization.

Typical error response:

{
  "error": true,
  "reason": "Description of the error."
}


Endpoints that return collections generally return JSON arrays. Some endpoints return pagination metadata alongside their results.

Authentication

The API uses Flask-Login for session-based authentication.

Public: No authentication required.
Authenticated: Requires a logged-in user.
Owner/editor: Requires permission to edit the relevant resource.
Admin: Requires administrator privileges.
Public profile: Some creation endpoints require the authenticated user's profile to be public.

Authenticated requests should use the application's login session. The login endpoint accepts form-encoded data.

Common data models
Mod

A mod represents a downloadable modification for a game.

Common fields include:

Field	Type	Description
id	integer	Mod ID
name	string	Mod name
game	string	Game name
game_id	integer	Game ID
short_description	string	Short description
downloads	integer	Download count
followers	integer	Follower count
author	string	Primary author's username
default_version_id	integer	Default version ID
shared_authors	array	Shared authors; populated by selected endpoints
background	string or null	Background image URL
bg_offset_y	integer or null	Background vertical offset
license	string or null	License identifier
website	string or null	External website
donations	string or null	Donation URL
source_code	string or null	Source repository URL
url	string	Relative URL to the mod page

Mod version objects contain:

Field	Type	Description
id	integer	Version ID
friendly_version	string	Mod version label
game_version	string	Supported game version
created	datetime	Version creation timestamp
download_path	string	Download URL
changelog	string or null	Changelog text
downloads	integer	Version download count
1. Game Endpoints
GET /api/kspversions

Description: Retired legacy endpoint. Use the game and game-version endpoints instead.

Authentication: Not required.

Response: HTTP 501 Not Implemented.

{
  "error": true,
  "reason": "This API call has been retired. Use /api/games to find the id of the game you want, then /api/<game_id>/versions to get its versions."
}

GET /api/games

Description: Returns all active games, ordered by name descending.

Authentication: Not required.

Response: Array of game objects.

[
  {
    "id": 1,
    "name": "Example Game",
    "publisher_id": 1,
    "short_description": "A short description",
    "description": "Full description",
    "created": "2025-01-01T00:00:00",
    "background": "game/background.jpg",
    "bg_offset_x": 0,
    "bg_offset_y": 0,
    "link": "https://example.com",
    "short": "example"
  }
]


Fields may contain null values depending on the stored game data.

GET /api/<gameid>/versions

Description: Returns the versions associated with a game.

Authentication: Not required.

Path parameters:

Parameter	Type	Description
gameid	string representing an ID	Game ID

Behavior:

Returns an empty array with HTTP 404 if the game does not exist or is inactive.
Versions are ordered by ID descending.

Response:

[
  {
    "id": 10,
    "friendly_version": "1.12.5"
  },
  {
    "id": 9,
    "friendly_version": "1.12.4"
  }
]

GET /api/<gameid>/categories

Description: Returns the category settings for a game.

Authentication: Not required.

Path parameters:

Parameter	Type	Description
gameid	string representing an ID	Game ID

Behavior:

Returns HTTP 404 and an empty array if the game does not exist or is inactive.
Categories are ordered by category ID ascending.
Includes settings even when a category is disabled.

Response:

[
  {
    "id": 1,
    "name": "Plugins",
    "icon": "plugin",
    "enabled": true,
    "notify": true
  }
]

GET /api/<gameid>/notifications

Description: Returns the notification definitions associated with a game.

Authentication: Not required.

Path parameters:

Parameter	Type	Description
gameid	string representing an ID	Game ID

Behavior:

Returns HTTP 404 and an empty array if the game does not exist or is inactive.

Response:

[
  {
    "id": 1,
    "name": "New build available",
    "builds_url": "https://example.com/builds",
    "add_url": "https://example.com/builds/add",
    "change_url": "https://example.com/builds/change"
  }
]


The builds_url, add_url, and change_url fields may be null.

2. Publisher Endpoints
GET /api/publishers

Description: Returns all publishers, ordered by ID descending.

Authentication: Not required.

Response:

[
  {
    "id": 1,
    "name": "Example Publisher",
    "short_description": "Short description",
    "description": "Full description",
    "created": "2025-01-01T00:00:00",
    "background": "publisher/background.jpg",
    "bg_offset_x": 0,
    "bg_offset_y": 0,
    "link": "https://example.com"
  }
]


Publisher fields may contain null values.

3. Mod Discovery and Search
GET /api/typeahead/mod

Description: Returns mod suggestions for autocomplete.

Authentication: Not required.

Query parameters:

Parameter	Type	Required	Description
game_id	string	No	Filter suggestions by game ID
query	string	No	Search text

Example:

GET /api/typeahead/mod?game_id=1&query=visual


Response: Array of mod objects, each including a versions array.

GET /api/search/mod

Description: Searches mods.

Authentication: Not required.

Query parameters:

Parameter	Type	Required	Description
query	string	No	Search text; defaults to an empty string
page	integer	No	Page number as interpreted by get_page()

Example:

GET /api/search/mod?query=visual&page=1


Response: Array of mod objects, each including a versions array.

The number of results passed to the search function is 30 per page.

GET /api/search/user

Description: Searches users and includes their published mods.

Authentication: Not required.

Query parameters:

Parameter	Type	Required	Description
query	string	No	Search text; defaults to an empty string
page	integer	No	Page number; defaults to 0 if absent or invalid

Example:

GET /api/search/user?query=example&page=0


Response:

[
  {
    "username": "example",
    "description": "User description",
    "forumUsername": "example_forum",
    "ircNick": "example",
    "twitterUsername": "example",
    "redditUsername": "example",
    "mods": []
  }
]


Only published mods are included in the mods array.

GET /api/browse

Description: Returns a paginated collection of published mods, optionally filtered by game or game version.

Authentication: Not required.

Query parameters:

Parameter	Type	Default	Description
count	integer	30	Results per page, clamped to 1–500
page	integer	1	Page number, minimum 1
game_id	integer	None	Filter by game ID
game_version	string	None	Filter by game-version label when game_id is supplied
game_version_id	integer	None	Filter by game-version ID
orderby	string	created	Sort field: name, updated, or default created
order	string	asc	Use desc for descending order; other values sort ascending

Example:

GET /api/browse?count=20&page=1&orderby=updated&order=desc&game_id=1


Filtering behavior:

Only published mods are returned.
If game_version_id is provided, it takes precedence over game_id and game_version.
game_version is only applied when game_id is provided.

Response:

{
  "total": 125,
  "count": 20,
  "pages": 7,
  "page": 1,
  "result": [
    {
      "id": 10,
      "name": "Example Mod",
      "versions": []
    }
  ]
}


Each object in result contains the standard mod fields and its version list. The example is abbreviated.

GET /api/browse/new

Description: Returns the newest published mods, ordered by creation time descending, using the application's pagination helper.

Authentication: Not required.

Query parameters:

Parameter	Type	Required	Description
game_id	integer	No	Filter by game
game_version	string	No	Filter by game-version label when game_id is supplied
game_version_id	integer	No	Filter by game-version ID

Example:

GET /api/browse/new?game_id=1


Response: Array of mod objects with version lists.

Pagination is applied internally. Unlike /api/browse, this endpoint does not return explicit pagination metadata.

GET /api/browse/top

Description: Returns the top mods according to the application's get_paginated_mods() helper.

Authentication: Not required.

Response: Array of mod objects with version lists.

The exact ranking and pagination behavior are defined by get_paginated_mods().

GET /api/browse/featured

Description: Returns featured mods ordered by featured priority descending.

Authentication: Not required.

Response: Array of mod objects with version lists.

Pagination is handled by paginate_query().

4. Authentication and User Account Endpoints
POST /api/login

Description: Authenticates a user and creates a Flask-Login session.

Authentication: Not required.

Content type: Form-encoded.

Request fields:

Field	Type	Required	Description
username	string	Yes	Username
password	string	Yes	Password

Example:

curl -X POST "https://your-domain.com/api/login" \
  -d "username=example" \
  -d "password=your-password"


Success response — HTTP 200:

{
  "error": false
}


Possible errors:

Status	Reason
401	Missing username or password
401	Username or password is incorrect
403	User is not confirmed

The username lookup is case-insensitive. Successful authentication establishes a session using login_user().

GET /api/user/<username>

Description: Returns a public user's profile and published mods.

Authentication: Not required.

Path parameters:

Parameter	Type	Description
username	string	Username

Response:

{
  "username": "example",
  "description": "User description",
  "forumUsername": "example_forum",
  "ircNick": "example",
  "twitterUsername": "example",
  "redditUsername": "example",
  "mods": []
}


Possible errors:

Status	Reason
404	User not found
403	User profile is not public

The profile response includes the user's published mods only.

POST /api/user/<username>/change-password

Description: Changes the authenticated user's password.

Authentication: Required. The username in the URL must match the logged-in user.

Content type: Form-encoded.

Request fields:

Field	Type	Required	Description
old-password	string	Yes in practice	Current password
new-password	string	Yes in practice	New password
new-password-confirm	string	Yes in practice	Confirmation of the new password

Example:

curl -X POST "https://your-domain.com/api/user/example/change-password" \
  -b cookies.txt \
  -d "old-password=old-password" \
  -d "new-password=new-password" \
  -d "new-password-confirm=new-password"


Success response:

{
  "error": false,
  "reason": "..."
}


Possible errors:

Status	Reason
403	The requester is not authorized to change this user's password
200	The old password does not match
200	The new password fails the password criteria

The password criteria are enforced by check_password_criteria(). The endpoint sends a password-change notification email after a successful update.

Note: Incorrect old passwords and invalid new passwords are returned as JSON errors without an explicit non-200 status in this implementation.

POST /api/user/<username>/delete

Description: Deletes a user account and associated files.

Authentication: Required.

Authorization: The user may delete their own account, or an administrator may delete another account.

Content type: Form-encoded.

Request fields:

Field	Type	Required	Description
username	string	Yes	Must exactly match the username in the URL

Example:

curl -X POST "https://your-domain.com/api/user/example/delete" \
  -b cookies.txt \
  -d "username=example"


Success response — HTTP 200:

{
  "error": false
}


Possible errors:

Status	Reason
401	Unauthorized
403	Submitted username does not match the URL
404	User does not exist

The endpoint attempts to remove the user's storage directory. If the deleted user is the currently logged-in user, their session is logged out.

5. Mod Information and Versions
GET /api/mod/<int:mod_id>

Description: Returns detailed information about a mod, including its description, rendered Markdown, shared authors, and versions.

Authentication: Not required for published mods.

Authorization for unpublished mods:

Unauthenticated requests receive HTTP 401.
Authenticated users other than the primary owner receive HTTP 403.
The primary owner may view their unpublished mod.

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID

Example:

GET /api/mod/123


Response: A mod object with additional fields.

{
  "id": 123,
  "name": "Example Mod",
  "game": "Example Game",
  "game_id": 1,
  "short_description": "Short description",
  "downloads": 100,
  "followers": 20,
  "author": "example",
  "default_version_id": 456,
  "shared_authors": [
    {
      "username": "coauthor",
      "description": "Co-author profile",
      "forumUsername": "",
      "ircNick": "",
      "twitterUsername": "",
      "redditUsername": ""
    }
  ],
  "background": null,
  "bg_offset_y": 0,
  "license": "MIT",
  "website": null,
  "donations": null,
  "source_code": null,
  "url": "/...",
  "versions": [],
  "description": "Full mod description",
  "description_html": "<p>Full mod description</p>"
}


The response is abbreviated. It contains the standard mod fields, an array of versions, accepted shared authors, the raw description, and the rendered HTML description.

Possible errors:

Status	Reason
401	Mod is unpublished and authentication is required
403	Mod is unpublished and the requester is not the owner
404	Mod not found
GET /api/mod/<int:mod_id>/<version>

Description: Returns details for a specific mod version.

Authentication: Not required for published mods.

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID
version	string	latest, latest_version, or a numeric version ID

Examples:

GET /api/mod/123/latest
GET /api/mod/123/latest_version
GET /api/mod/123/456


Behavior:

latest and latest_version return the mod's configured default version.
A numeric value is interpreted as a version ID belonging to the specified mod.
Unpublished mods are rejected.

Response:

{
  "friendly_version": "1.2.0",
  "game_version": "1.12.5",
  "id": 456,
  "created": "2025-01-01T00:00:00",
  "download_path": "/...",
  "changelog": "Bug fixes",
  "downloads": 10
}


Possible errors:

Status	Reason
400	Invalid version identifier
403	Mod is unpublished
404	Mod or version not found
GET /api/ksp-avc/<int:mod_id>

Description: Returns a KSP-AVC-compatible version manifest for a published mod.

Authentication: Not required.

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID

Example:

GET /api/ksp-avc/123


Response:

{
  "NAME": "Example Mod",
  "URL": "https://your-domain.com/api/ksp-avc/123",
  "DOWNLOAD": "https://your-domain.com/...",
  "CHANGE_LOG": "Bug fixes",
  "CHANGE_LOG_URL": "https://your-domain.com/...",
  "GITHUB": {
    "USERNAME": "example",
    "REPOSITORY": "example-mod"
  },
  "VERSION": "1.2.0",
  "KSP_VERSION": "1.12.5"
}


The GITHUB field is included only when the mod's source_link matches the supported GitHub repository URL pattern.

Possible errors:

Status	Reason
403	Mod is unpublished
404	Mod not found

This endpoint assumes that the mod has a valid default version and associated game version.

POST /api/download_counts

Description: Returns download counts for a supplied collection of published mod IDs.

Authentication: Not required.

Content type: Form-encoded.

Request fields:

Field	Type	Required	Description
mod_id	repeated string	No	One or more mod IDs

Example:

curl -X POST "https://your-domain.com/api/download_counts" \
  -d "mod_id=123" \
  -d "mod_id=456"


Response:

{
  "download_counts": [
    {
      "id": 123,
      "downloads": 100
    },
    {
      "id": 456,
      "downloads": 250
    }
  ]
}


Only published mods matching the submitted IDs are returned. Results are ordered by mod ID ascending.

6. Background Image Endpoints

All four endpoints accept an image upload using the form field image. Accepted file extensions are .png, .jpg, and .jpeg.

The application saves the image to configured storage, checks the uploaded file for malware, updates the resource's background path, and generates a thumbnail where applicable.

Common upload requirements:

Use multipart/form-data.
Send the image in the image field.
Configure the application's storage directory.
Have the required resource-editing permissions.

If the image is omitted or storage is not configured, the helper returns no new path. The route generally responds with {"path": null} in that case.

POST /api/mod/<int:mod_id>/update-bg

Description: Updates a mod's background image.

Authentication: Required.

Authorization: The requester must be allowed to edit the mod.

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID

Request: Multipart form with image.

Success response:

{
  "path": "https://your-domain.com/..."
}


The route also cleans up the old image and thumbnail where possible, generates a new thumbnail, and sends a change notification.

Possible errors: 400 for an unacceptable file extension or detected malware; 403 for insufficient editing rights; 404 if the mod does not exist.

POST /api/user/<username>/update-bg

Description: Updates a user's profile background.

Authentication: Required.

Authorization: The user must own the profile, or be an administrator.

Path parameters:

Parameter	Type	Description
username	string	Target username

Request: Multipart form with image.

Success response:

{
  "path": "https://your-domain.com/..."
}


Possible errors: 400 for an unacceptable file extension or detected malware; 403 for insufficient permissions; 404 if the user does not exist.

POST /api/pack/<int:pack_id>/update-bg

Description: Updates a mod pack's background image.

Authentication: Required.

Authorization: The requester must pass check_pack_editable() for the pack.

Path parameters:

Parameter	Type	Description
pack_id	integer	Pack ID

Request: Multipart form with image.

Success response:

{
  "path": "https://your-domain.com/..."
}


The route attempts to clean up the previous image and thumbnail and generates a replacement thumbnail.

Possible errors:

400 for an unacceptable file extension or detected malware.
403 when the requester cannot edit the pack.
Other exceptions are caught and returned in a JSON error response with HTTP 200 by this implementation.
POST /api/game/<int:game_id>/update-bg

Description: Updates a game's background image.

Authentication: Required.

Authorization: Administrator only.

Path parameters:

Parameter	Type	Description
game_id	integer	Game ID

Request: Multipart form with image.

Success response:

{
  "path": "https://your-domain.com/..."
}


Possible errors:

400 for an unacceptable file extension or detected malware.
404 if the game does not exist.
Other exceptions are caught and returned as JSON with HTTP 200.

Non-administrator users receive {"path": null} rather than an explicit authorization error.

7. Mod Author Management
POST /api/mod/<int:mod_id>/grant

Description: Invites another public user to become a shared author of a mod.

Authentication: The route uses mod-edit permission checks; it does not explicitly apply the @user_required decorator.

Authorization: The requester must pass _check_mod_editable().

Content type: Form-encoded.

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID

Request fields:

Field	Type	Required	Description
user	string	Yes	Username of the invited author

Example:

curl -X POST "https://your-domain.com/api/mod/123/grant" \
  -b cookies.txt \
  -d "user=coauthor"


Success response:

{
  "error": false
}


The new shared-author relationship starts with accepted = false. The application commits the invitation and sends a grant notification email.

Possible errors:

Status	Reason
400	User does not exist
400	User is already an author
400	User's profile is not public
403	Insufficient editing rights
404	Mod not found
POST /api/mod/<mod_id>/accept_grant

Description: Accepts a pending shared-author invitation.

Authentication: Required.

Path parameters:

Parameter	Type	Description
mod_id	string representing an ID	Mod ID

Success response:

{
  "error": false
}


The authenticated user must have a pending invitation. The endpoint marks the invitation as accepted and sends a change notification.

Possible errors: 403 for authentication or authorization failures, depending on the permission helper and response path; 404 if the mod does not exist.

An absent or already accepted invitation produces an error response with HTTP 200 in the implementation.

POST /api/mod/<mod_id>/reject_grant

Description: Rejects a pending shared-author invitation.

Authentication: Required.

Path parameters:

Parameter	Type	Description
mod_id	string representing an ID	Mod ID

Success response:

{
  "error": false
}


The authenticated user must have a pending invitation. The shared-author relationship is removed.

Possible errors: 403 for authentication or authorization failures, depending on the permission helper and response path; 404 if the mod does not exist.

An absent or already accepted invitation produces an error response with HTTP 200 in the implementation.

POST /api/mod/<int:mod_id>/revoke

Description: Removes a shared author from a mod.

Authentication: Required.

Authorization: The requester must pass _check_mod_editable().

Content type: Form-encoded.

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID

Request fields:

Field	Type	Required	Description
user	string	Yes	Username of the shared author to remove

Success response:

{
  "error": false
}


A change notification is sent after removing the shared author.

Possible errors:

Status	Reason
400	The primary owner cannot remove themselves
400	The specified user is not an author
403	Insufficient editing rights
404	Mod or specified user not found

Implementation note: The current implementation filters the shared-author list using a.user != current_user instead of a.user != new_user. This may remove the wrong relationship from the in-memory collection. The filtering condition should be reviewed.

8. Mod Version Management
POST /api/mod/<int:mod_id>/set-default/<int:vid>

Description: Sets the default version of a mod.

Authentication: The route uses mod-edit permission checks; it does not explicitly apply the @user_required decorator.

Authorization: The requester must pass _check_mod_editable().

Path parameters:

Parameter	Type	Description
mod_id	integer	Mod ID
vid	integer	Version ID

Example:

POST /api/mod/123/set-default/456


Success response:

{
  "error": false
}


Possible errors:

Status	Reason
403	Insufficient editing rights
404	Mod or specified version not found

The version must belong to the specified mod. A change notification is sent after the default version is updated.

POST /api/mod/create

Description: Creates a new unpublished mod and uploads its initial ZIP archive. The upload supports chunked transfers through Dropzone-style form fields.

Authentication: Required.

Authorization: The authenticated user's profile must be public.

Content type: multipart/form-data.

Request fields
Field	Type	Required	Description
name	string	Yes	Mod name; maximum 100 characters
short-description	string	Yes	Short description; maximum 1,000 characters
description	string	No	Full description; defaults to the built-in description
version	string	Yes	Initial mod version label
game-id	string/integer	Conditional	Game ID; preferred over the deprecated game field
game	string/integer	Conditional	Legacy game ID field
game-short-name	string	Conditional	Alternative game identifier when no game ID is supplied
game-version	string	Yes	Game version label
license	string	Yes	License identifier; maximum 128 characters
category	integer	Yes	Category ID enabled for the selected game
zipball	file	Yes per chunk	ZIP archive chunk
dztotalchunkcount	integer	No	Total number of upload chunks; defaults to 1
dzchunkindex	integer	No	Zero-based chunk index; defaults to 0
dzchunkbyteoffset	integer	No	Byte offset for writing the chunk; defaults to 0
notifications	repeated integer	No	Notification IDs to enable for the new mod

At least one of game-id, game, or game-short-name must identify the game. When game-id or game is present, that ID takes precedence over game-short-name.

Example
curl -X POST "https://your-domain.com/api/mod/create" \
  -b cookies.txt \
  -F "name=Example Mod" \
  -F "short-description=An example modification" \
  -F "description=Full description" \
  -F "version=1.0.0" \
  -F "game-id=1" \
  -F "game-version=1.12.5" \
  -F "license=MIT" \
  -F "category=1" \
  -F "zipball=@example-mod.zip"

Success response

When the final chunk has been processed, the response is HTTP 202:

{
  "url": "/...",
  "id": 123,
  "name": "Example Mod"
}


For intermediate chunks, the response is HTTP 202 with an empty JSON object:

{}

Validation and errors
Status	Reason
400	Required fields are missing
400	Fields exceed maximum permissible lengths
400	Game does not exist or is inactive
400	Game version does not exist
400	Category is invalid or disabled for the game
400	Uploaded archive is not a valid ZIP file
400	Malware detected in upload
403	User's profile is not public
202	Upload chunk accepted or mod created

The route validates the final ZIP archive and checks it for malware. It creates a mod with published = false and configures the initial version as the default. It does not send creation notifications because the mod is not yet published.

Implementation notes:

The upload helper depends on configured storage.
Chunk uploads are appended to a file. The client must provide consistent chunk metadata and offsets.
The request's notifications values are filtered against the selected game's available notification definitions.
POST /api/mod/<int:mod_id>/update

Description: Uploads a new version of an existing mod, including its ZIP archive and changelog.

Authentication: Required.

Authorization: The requester must be allowed to edit the mod.

Content type: multipart/form-data.

Request fields
Field	Type	Required	Description
version	string	Yes	New mod version label
game-version	string	Yes	Target game version label
changelog	string	No	Changelog in Markdown
zipball	file	Yes per chunk	ZIP archive chunk
dztotalchunkcount	integer	No	Total number of chunks; defaults to 1
dzchunkindex	integer	No	Zero-based chunk index; defaults to 0
dzchunkbyteoffset	integer	No	Byte offset for writing the chunk; defaults to 0
notify-followers	string	No	If its lowercase value matches TRUE_STR, notify followers
Example
curl -X POST "https://your-domain.com/api/mod/123/update" \
  -b cookies.txt \
  -F "version=1.1.0" \
  -F "game-version=1.12.5" \
  -F "changelog=Fixed bugs and improved performance" \
  -F "zipball=@example-mod-1.1.0.zip"

Success response

When the final chunk is processed:

{
  "url": "/...",
  "id": 789
}


The id is the newly created version ID. Intermediate chunks return HTTP 202 and an empty object.

Validation and errors
Status	Reason
400	Required fields are missing
400	Game version does not exist
400	Version label already exists for this mod
400	Changelog exceeds the column length limit
400	Rendered changelog exceeds the column length limit
400	Uploaded archive is not a valid ZIP file
400	Malware detected in upload
403	Insufficient editing rights
404	Mod not found
202	Chunk accepted or version created

The endpoint validates the game version against the mod's game, checks the archive for malware, creates a ModVersion, records its file size, makes it the default version, updates the mod's timestamp and score, and sends change notifications.

If notify-followers matches one of the accepted true strings, the endpoint also sends update notification emails to followers.

POST /api/mod/<int:mod_id>/edit_version

Description: Edits an existing version's changelog and optionally replaces its ZIP archive.

Authentication: Required.

Authorization: The requester must be allowed to edit the mod.

Content type: multipart/form-data.

Request fields
Field	Type	Required	Description
version-id	integer	Yes	ID of the version to edit
changelog	string	No	Updated Markdown changelog
zipball	file	Conditional	New ZIP archive chunk, when replacing the archive
dztotalchunkcount	integer	Conditional	Signals archive replacement and specifies total chunks
dzchunkindex	integer	No	Zero-based chunk index; defaults to 0
dzchunkbyteoffset	integer	No	Byte offset for writing the chunk; defaults to 0
Example: Update changelog only
curl -X POST "https://your-domain.com/api/mod/123/edit_version" \
  -b cookies.txt \
  -F "version-id=789" \
  -F "changelog=Updated documentation and fixed bugs"

Success response
{
  "url": "/..."
}


The returned URL points to the mod page's changelog section.

Validation and errors
Status	Reason
400	Changelog exceeds the column length limit
400	Rendered changelog exceeds the column length limit
400	Storage is not configured when replacing the archive
403	Insufficient editing rights
404	Mod or version not found
202	Changes accepted

When an archive replacement is requested, the endpoint removes the previous archive on the first chunk, purges the corresponding download cache, writes incoming chunks, and updates the version's size and creation timestamp when the last chunk arrives.

Implementation notes:

Unlike /api/mod/<mod_id>/update, this endpoint does not validate the uploaded archive with zipfile.is_zipfile() in the provided implementation.
The shown code does not run the malware scanner for replacement archives.
Chunk-upload clients should therefore follow the server's expected upload format and should not assume that all validation behavior is identical between the two endpoints.
9. HTTP Status Code Reference
Status	Meaning in this API
200 OK	Successful request; some application-level errors also use this status
202 Accepted	Chunk upload accepted or version operation processed
400 Bad Request	Invalid fields, version, category, archive, or upload
401 Unauthorized	Authentication required or invalid credentials
403 Forbidden	Authorization failure, unpublished resource, or private profile
404 Not Found	Resource or version not found
501 Not Implemented	Retired legacy endpoint

Important: Always inspect the JSON error field as well as the HTTP status. Several routes return {"error": true, ...} with HTTP 200.

10. Endpoint Index

The following is the complete route inventory found in the supplied api.py file.

Method	Endpoint	Purpose
GET	/api/kspversions	Retired legacy version endpoint
GET	/api/<gameid>/versions	List game versions
GET	/api/<gameid>/categories	List game category settings
GET	/api/<gameid>/notifications	List game notification definitions
GET	/api/games	List active games
GET	/api/publishers	List publishers
GET	/api/typeahead/mod	Mod autocomplete
GET	/api/search/mod	Search mods
GET	/api/search/user	Search users
GET	/api/browse	Paginated mod browsing
GET	/api/browse/new	Browse newest mods
GET	/api/browse/top	Browse top mods
GET	/api/browse/featured	Browse featured mods
POST	/api/login	Authenticate a user
GET	/api/mod/<int:mod_id>	Retrieve mod details
GET	/api/mod/<int:mod_id>/<version>	Retrieve a specific mod version
GET	/api/ksp-avc/<int:mod_id>	Retrieve KSP-AVC manifest
POST	/api/download_counts	Retrieve download counts
GET	/api/user/<username>	Retrieve a public user profile
POST	/api/user/<username>/change-password	Change account password
POST	/api/user/<username>/delete	Delete a user account
POST	/api/mod/<int:mod_id>/update-bg	Update mod background
POST	/api/user/<username>/update-bg	Update user background
POST	/api/pack/<int:pack_id>/update-bg	Update mod pack background
POST	/api/game/<int:game_id>/update-bg	Update game background
POST	/api/mod/<int:mod_id>/grant	Invite a shared author
POST	/api/mod/<mod_id>/accept_grant	Accept an author invitation
POST	/api/mod/<mod_id>/reject_grant	Reject an author invitation
POST	/api/mod/<int:mod_id>/revoke	Remove a shared author
POST	/api/mod/<int:mod_id>/set-default/<int:vid>	Set the default mod version
POST	/api/pack/create	Create a mod pack
POST	/api/mod/create	Create a mod and upload its initial version
POST	/api/mod/<int:mod_id>/update	Upload a new mod version
POST	/api/mod/<int:mod_id>/edit_version	Edit a version and optionally replace its archive
11. Notes and Limitations
This documentation covers api.py only. Other blueprints, route files, decorators, and helpers may define additional behavior or endpoints.
Some responses are abbreviated. Fields shown as ... or empty arrays are examples; actual values depend on database contents.
Pagination helpers are external. The precise pagination behavior of /api/search/mod, /api/browse/new, /api/browse/top, and /api/browse/featured depends on helper functions imported from other modules.
Session authentication is assumed. The endpoints use Flask-Login rather than an API token mechanism in the supplied code. For cookie-based authentication, clients must retain and send the appropriate session cookie.
Permission decorators differ between routes. Some endpoints explicitly use @user_required; others rely on _check_mod_editable() or perform their own checks. These should be reviewed when changing authentication or authorization behavior.
Chunked uploads require consistent metadata. The create and update routes write archive chunks to storage using the supplied offset and chunk index. Clients should use the same upload conventions as the application's Dropzone integration.
Database and serialization details may vary. SQLAlchemy models, JSON decorators, application configuration, and Flask URL configuration determine final serialization and generated URLs.
Potential implementation issues worth reviewing:
The revoke endpoint filters shared_authors against current_user instead of new_user.
Several routes use broad exception handling and return HTTP 200 for exceptions.
mod_info() assumes a default version exists.
The version-edit endpoint does not perform the same ZIP and malware checks as the new-version endpoint.
The @user_required decorator tests current_user rather than explicitly checking current_user.is_authenticated; depending on Flask-Login behavior, this may not correctly reject anonymous users.