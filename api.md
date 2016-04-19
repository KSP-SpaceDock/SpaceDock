# Kerbal Stuff API Docs

Kerbal Stuff has a simple HTTP API that you can use to do various interesting
things. Feel free to help make it better by submitting pull requests that update
[api.py](https://github.com/SirCmpwn/SpaceDock/blob/master/SpaceDock/blueprints/api.py).

## API Wrappers

* [Ruby API Wrapper, by RockyTV](https://github.com/RockyTV/KerbalStuffGem)
* [KerbalStuffWrapper, in C#, by toadicus.](http://forum.kerbalspaceprogram.com/threads/94891)

## Basics

Submit all POSTS with the request body encoded as
[multipart/form-data](https://www.ietf.org/rfc/rfc2388.txt). Your HTTP library
of choice probably handles that for you. All responses are JSON.

Changes to this API will happen occasionally and warning will be offered via an
email sent to all registered modders on the website and on the forum thread.

Please set your user agent to something that describes who you are and how to
contact the person operating the service.

**Note on mod backgrounds**: The background image for each mod is hosted on
https://mediacru.sh. The string returned in API requests is the path to that
image relative to cdn.mediacru.sh - so if the path was "/example.png", the
image can be found at "https://cdn.mediacru.sh/example.png".

### Errors

All requests that might fail include an `error` property in the response, which
is a boolean that will be true if the request failed. If the request failed, a
`reason` property will also be included that explains why it failed.

## Authentication

Some endpoints require authentication. To authenticate, use the login endpoint
and you will be given a cookie, which you should include in all subsequent
requests.

**POST /api/login**

Logs into Kerbal Stuff.

*Curl*

    curl -F username=SirCmpwn -F password=example -c ./cookies "https://spacedock.com/api/login"

*Parameters*

* `username`
* `password`

*Example Response*

Successful login:

    {
        "error": false
    }

Failed login:

    {
        "error": true,
        "reason": "Username or password is incorrect"
    }

## Browse

You can browse the site without authentication.

**GET /api/browse?page=&lt;integer&gt;&orderby=&lt;string&gt;&order=&lt;string&gt;&count=&lt;integer&gt;**

Gets mods sorted by selected conditions

*Curl*

    curl "https://spacedock.com/api/browse"

*Parameters*

* `page`: Which page of results to retrieve (1 indexed) [*optional*]
* `orderby`: Which property of mod use for ordering. Valid values: name, updated, created. Default: created. [*optional*]
* `order`: Which ordering direction to use. Valid values: asc, desc. Default: asc. [*optional*]
* `count`: Which count of mods to show per page. Valid values: 1-500. Default 30. [*optional*]

*Example Response*:

    {
      "result": [
        {
          "downloads": 27885,
          "name": "Ferram Aerospace Research",
          "followers": 177,
          "author": "ferram4",
          "default_version_id": 295,
          "versions": [
            {
              "changelog": "...",
              "game_version": "0.24.2",
              "download_path": "/mod/52/Ferram%20Aerospace%20Research/download/v0.14.1.1",
              "id": 151,
              "friendly_version": "v0.14.1.1"
            }
          ],
          "id": 52,
          "background": "...",
          "bg_offset_y": 1234,
          "short_description": "..."
        },
        ...continued...
      ],
      "count": 30,
      "pages": 100,
      "page": 1
    }

**GET /api/browse/new?page=&lt;integer&gt;**

Gets the newest mods on the site.

*Curl*

    curl "https://spacedock.com/api/browse/new"

*Parameters*

* `page`: Which page of results to retrieve (1 indexed) [*optional*]

*Example Response*:

    [
      {
        "downloads": 27885,
        "name": "Ferram Aerospace Research",
        "followers": 177,
        "author": "ferram4",
        "default_version_id": 295,
        "versions": [
          {
            "changelog": "...",
            "game_version": "0.24.2",
            "download_path": "/mod/52/Ferram%20Aerospace%20Research/download/v0.14.1.1",
            "id": 151,
            "friendly_version": "v0.14.1.1"
          }
        ],
        "id": 52,
        "background": "...",
        "bg_offset_y": 1234,
        "short_description": "..."
      },
      ...continued...
    ]


**GET /api/browse/featured?page=&lt;integer&gt;**

Gets the latest featured mods on the site.

*Curl*

    curl "https://spacedock.com/api/browse/featured"

*Parameters*

* `page`: Which page of results to retrieve (1 indexed) [*optional*]

*Example Response*:

    [
      {
        "downloads": 27885,
        "name": "Ferram Aerospace Research",
        "followers": 177,
        "author": "ferram4",
        "default_version_id": 295,
        "versions": [
          {
            "changelog": "...",
            "game_version": "0.24.2",
            "download_path": "/mod/52/Ferram%20Aerospace%20Research/download/v0.14.1.1",
            "id": 151,
            "friendly_version": "v0.14.1.1"
          }
        ],
        "id": 52,
        "background": "...",
        "bg_offset_y": 1234,
        "short_description": "..."
      },
      ...continued...
    ]

**GET /api/browse/top?page=&lt;integer&gt;**

Gets the most popular mods on the site.

*Curl*

    curl "https://spacedock.com/api/browse/top"

*Parameters*

* `page`: Which page of results to retrieve (1 indexed) [*optional*]

*Example Response*:

    [
      {
        "downloads": 27885,
        "name": "Ferram Aerospace Research",
        "followers": 177,
        "author": "ferram4",
        "default_version_id": 295,
        "versions": [
          {
            "changelog": "...",
            "game_version": "0.24.2",
            "download_path": "/mod/52/Ferram%20Aerospace%20Research/download/v0.14.1.1",
            "id": 151,
            "friendly_version": "v0.14.1.1"
          }
        ],
        "id": 52,
        "background": "...",
        "bg_offset_y": 1234,
        "short_description": "..."
      },
      ...continued...
    ]

## Search

You can search the site without authentication.

**GET /api/search/mod?query=&lt;name&gt;**

Searches the site for mods.

*Curl*

    curl "https://spacedock.com/api/search/mod?query=FAR"

*Parameters*

* `query`: Search terms
* `page`: Which page of results to retrieve (1 indexed) [*optional*]

*Example Response*:

    [
      {
        "downloads": 27885,
        "name": "Ferram Aerospace Research",
        "followers": 177,
        "author": "ferram4",
        "default_version_id": 295,
        "versions": [
          {
            "changelog": "...",
            "game_version": "0.24.2",
            "download_path": "/mod/52/Ferram%20Aerospace%20Research/download/v0.14.1.1",
            "id": 151,
            "friendly_version": "v0.14.1.1"
          }
        ],
        "id": 52,
        "background": "...",
        "bg_offset_y": 1234,
        "short_description": "..."
      }
    ]

**GET /api/search/user?query=&lt;name&gt;**

Searches the site for public users.

*Curl*

    curl "https://spacedock.com/api/search/user?query=sircmpwn"

*Parameters*

* `query`: Search terms
* `page`: Which page of results to retrieve (1 indexed) [*optional*]

*Example Response*

    [
      {
        "username": "SirCmpwn",
        "twitterUsername": "sircmpwn",
        "mods": [],
        "redditUsername": "",
        "ircNick": "sircmpwn",
        "description": "Hi, I made this website.",
        "forumUsername": "SirCmpwn"
      }
    ]

## Users

You can query the API for information on individual public users.

**GET /api/user/&lt;username&gt;**

Returns information about a specific user.

*Curl*

    curl "https://spacedock.com/api/user/Xaiier"

*Example Response*

    {
      "username": "Xaiier",
      "twitterUsername": "",
      "mods": [
        {
          "downloads": 332,
          "name": "Time Control",
          "followers": 19,
          "author": "Xaiier",
          "default_version_id": 371,
          "id": 21,
          "short_description": "..."
        }
      ],
      "redditUsername": null,
      "ircNick": "Xaiier",
      "description": "",
      "forumUsername": "Xaiier"
    }

## Mods

You can query the API for information on a specific mod, a specific version, and
so on. This could be useful, for example, to implement an update checker. You can
also use the API to create new mods or update existing ones.

**GET /api/mod/&lt;mod_id&gt;**

Returns information about a specific mod.

*Curl*

    curl "https://spacedock.com/api/mod/21"

*Example Response*

    {
      "downloads": 332,
      "name": "Time Control",
      "followers": 19,
      "author": "Xaiier",
      "default_version_id": 371,
      "versions": [
        {
          "changelog": "...",
          "game_version": "0.24.2",
          "download_path": "/mod/21/Time%20Control/download/13.0",
          "id": 371,
          "friendly_version": "13.0"
        }
      ],
      "background": "...",
      "bg_offset_y": 1234,
      "description:" "...markdown...",
      "description_html": "...html...",
      "id": 21,
      "short_description": "...",
      "updated": "...date/time..."
    }

**GET /api/mod/&lt;mod_id&gt;/latest**

Returns the latest version of a mod.

*Curl*

    curl "https://spacedock.com/api/mod/21/latest"

*Example Response*

    {
      "changelog": "...",
      "game_version": "0.24.2",
      "download_path": "/mod/21/Time%20Control/download/13.0",
      "id": 371,
      "friendly_version": "13.0"
    }

**POST /api/mod/create**

Creates a new mod. **Requires authentication**.

*Curl*

    curl -c ./cookies \
        -F" name=Example Mod" \
        -F "short-description=this is your schort description" \
        -F "version=1.0" \
        -F "game-version=0.24" \
        -F "license=GPLv2" \
        -F "zipball=@ExampleMod.zip" \
        "https://spacedock.com/api/mod/create"

*Parameters*

* `name`: Your new mod's name
* `short-description`: Short description of your mod
* `version`: The latest friendly version of your mod
* `game-version`: The Game version this is compatible with
* `license`: Your mod's license
* `ckan`: If "yes", automatically add your mod to the CKAN index
* `zipball`: The actual mod's zip file

*Example Response*

    {
      "url": "/mod/1234/Example Mod"
    }

*Notes*

This creates an unpublished mod. You must log into the actual site to publish
your mod.

**POST /api/mod/&lt;mod_id&gt;/update**

Publishes an update to an existing mod. **Requires authentication**.

*Curl*

    curl -c ./cookies \
        -F "version=1.0" \
        -F "changelog=this is your changelog" \
        -F "game-version=0.24" \
        -F "notify-followers=yes" \
        -F "zipball=@ExampleMod.zip" \
        "https://spacedock.com/api/mod/1234/update"

*Parameters*

* `version`: The friendly version number about to be created
* `changelog`: Markdown changelog
* `game-version`: The version of KSP this is compatible with
* `notify-followers`: If "yes", email followers about this update
* `zipball`: The actual mod's zip file

## KSPVersions

**GET /api/kspversions**

This will list the configured KSPVersions on the SpaceDock Site.

*Curl*

    curl "https://spacedock.com/api/kspversions"

*Example Response*:

    [
        {
          "id": 763,
          "friendly_version": "0.25"
        },
        {
          "id": 743,
          "friendly_version": "0.24.1"
        },
        ...continued...
	]
