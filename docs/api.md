# SpaceDock API Documentation

This document provides comprehensive documentation for the SpaceDock API endpoints, usage guidelines, and best practices.

## API Overview

SpaceDock provides a RESTful API for interacting with mods, users, and other resources. The API is designed to be simple, consistent, and well-documented.

### Base URL

```
https://spacedock.info/api
```

### Authentication

Most API endpoints require authentication. Use the following methods:

#### API Key Authentication

Include your API key in the request headers:
# SpaceDock API Documentation

This document provides comprehensive documentation for the SpaceDock API endpoints, usage guidelines, and best practices.

## API Overview

SpaceDock provides a RESTful API for interacting with mods, users, and other resources. The API is designed to be simple, consistent, and well-documented.

### Base URL

```
https://spacedock.info/api
```

### Authentication

Most API endpoints require authentication. Use the following methods:

#### API Key Authentication

Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

#### Session Authentication

For web-based applications, use session cookies:

```
# No additional headers required
```

### Rate Limiting

The API enforces rate limiting to prevent abuse:

- **Anonymous users**: 60 requests per minute
- **Authenticated users**: 300 requests per minute

Exceeding the rate limit will result in a `429 Too Many Requests` response.

### Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no content
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with details:

```json
{
  "error": "Invalid request",
  "message": "The provided data was invalid.",
  "details": {
    "field": ["Error message for field"]
  }
}
```

## API Endpoints

### Mods

#### List Mods

```http
GET /api/mods
```

**Parameters:**

- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search query
- `game_version` (optional): Filter by game version
- `sort` (optional): Sort field (e.g., `name`, `downloads`, `updated`)
- `order` (optional): Sort order (`asc` or `desc`)

**Response:**

```json
{
  "mods": [
    {
      "id": 1,
      "name": "Example Mod",
      "description": "A mod for Kerbal Space Program",
      "downloads": 1000,
      "updated": "2023-01-01T00:00:00Z",
      "game_versions": ["1.12.3"],
      "author": {
        "id": 1,
        "name": "Author Name"
      }
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

#### Get Mod Details

```http
GET /api/mods/{id}
```

**Response:**

```json
{
  "id": 1,
  "name": "Example Mod",
  "description": "A mod for Kerbal Space Program",
  "downloads": 1000,
  "updated": "2023-01-01T00:00:00Z",
  "game_versions": ["1.12.3"],
  "author": {
    "id": 1,
    "name": "Author Name"
  },
  "versions": [
    {
      "id": 1,
      "version": "1.0.0",
      "download_url": "https://example.com/mod.zip",
      "changelog": "Initial release",
      "game_versions": ["1.12.3"]
    }
  ]
}
```

#### Create Mod

```http
POST /api/mods
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Body:**

```json
{
  "name": "Example Mod",
  "description": "A mod for Kerbal Space Program",
  "game_versions": ["1.12.3"]
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Example Mod",
  "description": "A mod for Kerbal Space Program",
  "game_versions": ["1.12.3"]
}
```

#### Update Mod

```http
PUT /api/mods/{id}
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Body:**

```json
{
  "name": "Updated Mod Name",
  "description": "Updated description"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Updated Mod Name",
  "description": "Updated description"
}
```

#### Delete Mod

```http
DELETE /api/mods/{id}
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
```

**Response:**

```json
{
  "message": "Mod deleted successfully"
}
```

### Users

#### Get User Profile

```http
GET /api/users/{id}
```

**Response:**

```json
{
  "id": 1,
  "name": "User Name",
  "username": "username",
  "avatar": "https://example.com/avatar.jpg",
  "mods": [
    {
      "id": 1,
      "name": "Example Mod"
    }
  ]
}
```

#### Get Current User

```http
GET /api/users/me
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
```

**Response:**

```json
{
  "id": 1,
  "name": "User Name",
  "username": "username",
  "avatar": "https://example.com/avatar.jpg"
}
```

### Lists

#### List User Lists

```http
GET /api/users/{id}/lists
```

**Response:**

```json
{
  "lists": [
    {
      "id": 1,
      "name": "My Favorite Mods",
      "description": "A list of my favorite mods",
      "mods": [
        {
          "id": 1,
          "name": "Example Mod"
        }
      ]
    }
  ]
}
```

#### Create List

```http
POST /api/lists
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Body:**

```json
{
  "name": "My Favorite Mods",
  "description": "A list of my favorite mods"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "My Favorite Mods",
  "description": "A list of my favorite mods"
}
```

### Game Versions

#### List Game Versions

```http
GET /api/game_versions
```

**Response:**

```json
{
  "game_versions": [
    {
      "id": 1,
      "name": "1.12.3",
      "display_name": "1.12.3"
    }
  ]
}
```

## API Clients

### Python Client

```python
import requests

BASE_URL = "https://spacedock.info/api"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# List mods
response = requests.get(f"{BASE_URL}/mods", headers=
```
Authorization: Bearer YOUR_API_KEY
```

#### Session Authentication

For web-based applications, use session cookies:

```
# No additional headers required
```

### Rate Limiting

The API enforces rate limiting to prevent abuse:

- **Anonymous users**: 60 requests per minute
- **Authenticated users**: 300 requests per minute

Exceeding the rate limit will result in a `429 Too Many Requests` response.

### Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no content
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON body with details:

```json
{
  "error": "Invalid request",
  "message": "The provided data was invalid.",
  "details": {
    "field": ["Error message for field"]
  }
}
```

## API Endpoints

### Mods

#### List Mods

```http
GET /api/mods
```

**Parameters:**

- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search query
- `game_version` (optional): Filter by game version
- `sort` (optional): Sort field (e.g., `name`, `downloads`, `updated`)
- `order` (optional): Sort order (`asc` or `desc`)

**Response:**

```json
{
  "mods": [
    {
      "id": 1,
      "name": "Example Mod",
      "description": "A mod for Kerbal Space Program",
      "downloads": 1000,
      "updated": "2023-01-01T00:00:00Z",
      "game_versions": ["1.12.3"],
      "author": {
        "id": 1,
        "name": "Author Name"
      }
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

#### Get Mod Details

```http
GET /api/mods/{id}
```

**Response:**

```json
{
  "id": 1,
  "name": "Example Mod",
  "description": "A mod for Kerbal Space Program",
  "downloads": 1000,
  "updated": "2023-01-01T00:00:00Z",
  "game_versions": ["1.12.3"],
  "author": {
    "id": 1,
    "name": "Author Name"
  },
  "versions": [
    {
      "id": 1,
      "version": "1.0.0",
      "download_url": "https://example.com/mod.zip",
      "changelog": "Initial release",
      "game_versions": ["1.12.3"]
    }
  ]
}
```

#### Create Mod

```http
POST /api/mods
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Body:**

```json
{
  "name": "Example Mod",
  "description": "A mod for Kerbal Space Program",
  "game_versions": ["1.12.3"]
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Example Mod",
  "description": "A mod for Kerbal Space Program",
  "game_versions": ["1.12.3"]
}
```

#### Update Mod

```http
PUT /api/mods/{id}
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Body:**

```json
{
  "name": "Updated Mod Name",
  "description": "Updated description"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "Updated Mod Name",
  "description": "Updated description"
}
```

#### Delete Mod

```http
DELETE /api/mods/{id}
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
```

**Response:**

```json
{
  "message": "Mod deleted successfully"
}
```

### Users

#### Get User Profile

```http
GET /api/users/{id}
```

**Response:**

```json
{
  "id": 1,
  "name": "User Name",
  "username": "username",
  "avatar": "https://example.com/avatar.jpg",
  "mods": [
    {
      "id": 1,
      "name": "Example Mod"
    }
  ]
}
```

#### Get Current User

```http
GET /api/users/me
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
```

**Response:**

```json
{
  "id": 1,
  "name": "User Name",
  "username": "username",
  "avatar": "https://example.com/avatar.jpg"
}
```

### Lists

#### List User Lists

```http
GET /api/users/{id}/lists
```

**Response:**

```json
{
  "lists": [
    {
      "id": 1,
      "name": "My Favorite Mods",
      "description": "A list of my favorite mods",
      "mods": [
        {
          "id": 1,
          "name": "Example Mod"
        }
      ]
    }
  ]
}
```

#### Create List

```http
POST /api/lists
```

**Headers:**

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Body:**

```json
{
  "name": "My Favorite Mods",
  "description": "A list of my favorite mods"
}
```

**Response:**

```json
{
  "id": 1,
  "name": "My Favorite Mods",
  "description": "A list of my favorite mods"
}
```

### Game Versions

#### List Game Versions

```http
GET /api/game_versions
```

**Response:**

```json
{
  "game_versions": [
    {
      "id": 1,
      "name": "1.12.3",
      "display_name": "1.12.3"
    }
  ]
}
```

## API Clients

### Python Client

```python
import requests

BASE_URL = "https://spacedock.info/api"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# List mods
response = requests.get(f"{BASE_URL}/mods", headers=