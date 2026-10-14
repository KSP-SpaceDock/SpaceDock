# SpaceDock Tests Rules

This file provides comprehensive guidelines for writing and maintaining tests in the SpaceDock project.

## Test Organization

### Directory Structure

- `tests/` - Main test directory
  - `unit/` - Unit tests for individual components
  - `integration/` - Integration tests for API endpoints
  - `functional/` - Functional tests for user flows
  - `fixtures/` - Test fixtures and data
  - `conftest.py` - Global test configuration

### Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`
- Fixtures should be named with `*` prefix (e.g., `user_fixture`)

## Writing Tests

### Unit Tests

Unit tests should focus on individual functions or methods in isolation.

```python
def test_add_numbers():
    result = add_numbers(2, 3)
    assert result == 5
```

### Integration Tests

Integration tests should verify interactions between components.

```python
def test_mod_creation(client, db_session):
    response = client.post('/api/mods', 
                           data={'name': 'Test Mod'})
    assert response.status_code == 201
    assert Mod.query.count() == 1
```

### Functional Tests

Functional tests should simulate user interactions and verify complete workflows.

```python
def test_user_registration_and_login(client):
    # Register a new user
    response = client.post('/register', 
                           data={'username': 'testuser', 
                                 'email': 'test@example.com',
                                 'password': 'password123'})
    assert response.status_code == 302

    # Login with the new user
    response = client.post('/login',
                           data={'username': 'testuser',
                                 'password': 'password123'})
    assert response.status_code == 302
```

## Test Fixtures

Fixtures provide test data and setup/teardown functionality.

```python
import pytest
from KerbalStuff.objects import User, Mod

@pytest.fixture
def test_user(db_session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_mod(db_session, test_user):
    mod = Mod(name='Test Mod', author=test_user)
    db_session.add(mod)
    db_session.commit()
    return mod
```

## Mocking Strategies

Use mocking to isolate tests from external services.

```python
def test_send_email_mocking(mocker):
    mock_send = mocker.patch('KerbalStuff.email.send_email')
    
    # Call function that sends email
    send_welcome_email('test@example.com')
    
    # Verify email was sent
    mock_send.assert_called_once_with('test@example.com', 'Welcome', '...')
```

## Best Practices

1. **Test Coverage**: Aim for 80%+ coverage for critical paths
2. **Isolation**: Tests should be independent and not rely on each other
3. **Speed**: Keep tests fast to encourage frequent running
4. **Readability**: Use descriptive test names and clear assertions
5. **Maintainability**: Update tests when code changes

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/unit/test_user.py

# Run specific test method
python -m pytest tests/unit/test_user.py::test_user_creation

# Run tests with coverage
python -m pytest tests/ --cov=KerbalStuff

# Run tests with verbose output
python -m pytest tests/ -v
```

## Continuous Integration

Tests are automatically run on every push and pull request. Ensure your tests pass before submitting changes.

## Debugging Tests

```bash
# Run tests in debug mode
python -m pytest tests/ -v -s

# Run a single test with pdb
python -m pytest tests/unit/test_user.py::test_user_creation -v -s --pdb
```

For questions about testing, refer to this file or consult the team.