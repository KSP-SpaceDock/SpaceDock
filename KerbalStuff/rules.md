# KerbalStuff Module Rules

This file provides comprehensive guidelines for working with the KerbalStuff module, which contains the core application logic for SpaceDock.

## Module Overview

The `KerbalStuff` module is the main application package for SpaceDock. It contains:
- Flask application configuration and setup
- Database models and ORM
- Core business logic
- Blueprints for routing
- Utility functions and helpers
- Email and notification systems
- Celery task configuration

## Directory Structure

```
KerbalStuff/
├── __init__.py              # Package initialization
├── app.py                  # Flask application setup
├── blueprints/             # Application blueprints (routes and views)
├── objects.py              # Database models
├── database.py             # Database configuration
├── config.py               # Configuration management
├── celery.py               # Celery task configuration
├── email.py                # Email sending functionality
├── helpers.py              # Utility functions
├── kerbdown.py             # Markdown processor
├── notification.py         # Notification system
├── search.py               # Search functionality
├── thumbnail.py            # Thumbnail generation
├── antivirus.py            # Antivirus scanning
├── purge.py                # Cache purging
├── profiling.py            # Performance profiling
├── middleware/             # Custom middleware
└── custom_json.py          # Custom JSON encoder
```

## Core Components

### Flask Application Setup (`app.py`)

**Responsibilities:**
- Initialize the Flask application
- Register blueprints
- Configure extensions (database, caching, etc.)
- Set up error handlers
- Configure logging

**Best Practices:**
- Keep application initialization clean and modular
- Use application factories for better testability
- Configure extensions early in the application lifecycle
- Set up error handlers for consistent error responses

### Database Models (`objects.py`)

**Responsibilities:**
- Define SQLAlchemy models for all database entities
- Implement model relationships
- Add model methods and properties
- Handle database migrations

**Best Practices:**
- Use SQLAlchemy's declarative base for model definitions
- Define relationships explicitly
- Add appropriate indexes for performance
- Use model methods for business logic
- Implement `__repr__` for debugging

### Blueprints (`blueprints/`)

**Responsibilities:**
- Organize routes and views by feature
- Handle HTTP requests and responses
- Implement authentication and authorization
- Process form submissions

**Best Practices:**
- Keep blueprints focused on a single feature
- Use consistent route naming conventions
- Implement proper error handling
- Use decorators for authentication and authorization
- Keep views thin and move logic to services

### Configuration (`config.py`)

**Responsibilities:**
- Load configuration from various sources (files, environment variables)
- Provide default values
- Validate configuration

**Best Practices:**
- Use environment variables for sensitive data
- Provide sensible defaults
- Validate configuration on startup
- Document required configuration options

### Email System (`email.py`)

**Responsibilities:**
- Send transactional emails
- Generate email templates
- Handle email queues

**Best Practices:**
- Use templates for email content
- Implement async email sending with Celery
- Handle email failures gracefully
- Respect user preferences for email notifications

### Celery Tasks (`celery.py`)

**Responsibilities:**
- Define background tasks
- Configure Celery workers
- Handle task queues

**Best Practices:**
- Use tasks for long-running operations
- Implement retry logic for failed tasks
- Use task timeouts to prevent hanging
- Monitor task queues for performance

## Development Guidelines

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and modular
- Write comprehensive docstrings
- Include tests for new functionality

### Database Changes

1. **Define the model change** in `objects.py`
2. **Create a migration** with Alembic:
   ```bash
   alembic revision -m "message"
   ```
3. **Edit the migration** file to implement the schema change
4. **Test the migration** in a development environment
5. **Apply the migration** to production

### Adding New Features

1. **Create a new blueprint** in `blueprints/`
2. **Define routes and views**
3. **Add necessary models** to `objects.py`
4. **Implement business logic** in helper functions
5. **Add tests** in the `tests/` directory
6. **Update documentation** as needed

### Error Handling

- Use consistent error responses
- Log errors appropriately
- Provide user-friendly error messages
- Implement custom error pages

### Security

- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization
- Use secure cookies for sessions
- Sanitize output to prevent XSS

### Performance

- Use database indexes appropriately
- Implement caching where needed
- Use pagination for large result sets
- Optimize queries to avoid N+1 problems
- Use Celery for background tasks

## Common Tasks

### Adding a New Model

1. Define the model in `objects.py`:
   ```python
   class NewModel(Base):
       __tablename__ = 'new_model'
       
       id = Column(Integer, primary_key=True)
       name = Column(String(100), nullable=False)
       created_at = Column(DateTime, server_default=func.now())
       
       def __repr__(self):
           return f'<NewModel {self.name}>'
   ```

2. Create a migration:
   ```bash
   alembic revision -m "add new_model table"
   ```

3. Edit the migration file to create the table.

4. Apply the migration:
   ```bash
   alembic upgrade head
   ```

### Adding a New Route

1. Create or edit a blueprint in `blueprints/`:
   ```python
   from flask import Blueprint, render_template
   
   new_blueprint = Blueprint('new_blueprint', __name__)
   
   @new_blueprint.route('/new-route')
   def new_route():
       return render_template('new_route.html')
   ```

2. Register the blueprint in `app.py`:
   ```python
   from .blueprints.new_blueprint import new_blueprint
   
   app.register_blueprint(new_blueprint)
   ```

3. Create a template in `templates/new_route.html`.

### Adding a Background Task

1. Define the task in `celery.py`:
   ```python
   @celery.task(bind=True, max_retries=3)
   def process_data(self, data):
       try:
           # Process data
           return result
       except Exception as exc:
           self.retry(exc=exc, countdown=60)
   ```

2. Call the task from your application:
   ```python
   from .celery import process_data
   
   process_data.delay(data)
   ```

## Testing

### Unit Tests

Write unit tests for individual functions and methods:
```python
from tests import TestCase
from KerbalStuff.objects import User

class TestUserModel(TestCase):
    def test_user_creation(self):
        user = User(username='testuser', email='test@example.com')
        self.assertEqual(user.username, 'testuser')
```

### Integration Tests

Write integration tests for API endpoints:
```python
from tests import TestCase

class TestModAPI(TestCase):
    def test_get_mods(self):
        response = self.client.get('/api/mods')
        self.assertEqual(response.status_code, 200)
```

### Functional Tests

Write functional tests for user flows:
```python
from tests import TestCase

class TestUserRegistration(TestCase):
    def test_register_and_login(self):
        # Register
        response = self.client.post('/register', data={'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        
        # Login
        response = self.client.post('/login', data={'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Flask-Login Documentation](https://