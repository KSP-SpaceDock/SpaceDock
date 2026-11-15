# SpaceDock Test Suite

## Overview

The SpaceDock test suite uses pytest with the Flask test client. Tests run in a Docker Compose development environment with an ephemeral database populated with test data.

## Running Tests

### From host machine

```bash
docker compose up -d --build backend
docker compose exec backend python -m pytest tests/ -v --tb=short
```

### In development container

```bash
python -m pytest tests/ -v
```

### Specific test files

```bash
# Run only API tests
docker compose exec backend python -m pytest tests/test_api_mods.py -v

# Run only legacy compatibility tests
docker compose exec backend python -m pytest tests/test_api_legacy.py -v

# Run basic smoke tests
docker compose exec backend python -m pytest tests/test_basic.py -v
```

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures: test DB setup, client fixture
├── test_basic.py        # Smoke tests: DB connection, users exist
├── test_api_auth.py     # Authentication: login, logout
├── test_api_games.py    # Game routes: list, info, legacy redirects
├── test_pages.py        # Frontend page availability tests (HTTP-level)
├── test_api_users.py    # User routes: info, search
└── test_api_publishers.py # Publisher routes
```

## Fixtures

### `app`
Flask application instance with test configuration. Creates an in-memory SQLite database.

### `client`
Flask test client for making HTTP requests.

### `db_session`
Database session for direct DB operations in tests.

## Writing New Tests

### API Test Template

```python
import json

def test_my_endpoint(client):
    """Test description."""
    # Make request
    response = client.get('/api/game/1/mods/browse/all')
    
    # Check status
    assert response.status_code == 200
    
    # Parse response
    data = json.loads(response.data)
    
    # Assert response structure
    assert 'page' in data
    assert 'pages' in data
    assert 'mods' in data
```

### Legacy Compatibility Test Template

```python
def test_legacy_compatibility(client):
    """Ensure legacy routes return compatible response format."""
    # Legacy route
    legacy = client.get('/api/browse')
    legacy_data = json.loads(legacy.data)
    
    # New route
    new = client.get('/api/game/1/mods/browse/all')
    new_data = json.loads(new.data)
    
    # Compare structure
    legacy_keys = set(legacy_data.keys())
    new_keys = set(new_data.keys())
    missing = legacy_keys - new_keys
    assert not missing, f"New route missing fields: {missing}"
```

## Test Data

The Docker Compose development environment populates the database with:
- 50 test users
- Multiple games with versions
- Mods across various games and categories
- Download and follow events

Test data is regenerated on each container restart via the `spacedock database populate` command.

## Test Philosophy

1. **Integration over unit**: Tests exercise the full HTTP stack through the Flask test client
2. **Legacy compatibility**: All legacy routes are tested to ensure backward compatibility
3. **Response structure**: Tests verify response field names and types
4. **Error handling**: Tests verify correct HTTP status codes for error cases
5. **Database-backed**: Tests run against a real (ephemeral) PostgreSQL database

## Adding New Endpoints

When adding a new API endpoint:

1. Write test in appropriate test file
2. Test happy path (200 status, correct structure)
3. Test error cases (404, 403, 400)
4. Test legacy compatibility if applicable
5. Run full test suite to ensure no regressions