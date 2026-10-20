# SpaceDock CONTINUE.md

This file provides comprehensive documentation for working with the SpaceDock codebase.

## Project Overview

SpaceDock is a website engine for hosting game mods, specifically designed for Kerbal Space Program. It's a Flask-based web application with a Python backend and JavaScript frontend that allows users to upload, share, and manage game modifications.

### Key Technologies
- **Backend**: Python 3 with Flask web framework
- **Frontend**: JavaScript, CoffeeScript, HTML/CSS with Twig templates
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Authentication**: Flask-Login
- **Build System**: Node.js/NPM for frontend assets
- **Testing**: pytest

### Architecture
SpaceDock follows a standard Flask application architecture:
- `KerbalStuff/` - Main application package
- `templates/` - Twig templates for frontend views
- `frontend/` - Frontend assets (JavaScript, CSS, CoffeeScript)
- `tests/` - Test suite
- `alembic/` - Database migrations

## Getting Started

### Prerequisites

To develop SpaceDock, you'll need:

**System Dependencies:**
- Python 3.8+ (python3, python3-dev)
- Node.js 16+ and npm
- PostgreSQL 12+
- Redis
- uWSGI (for production)

**Python Packages:**
- Flask and Flask extensions
- SQLAlchemy
- Celery
- psycopg2-binary
- Various other dependencies listed in requirements files

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KSP-SpaceDock/SpaceDock.git
   cd SpaceDock
   ```

2. **Set up virtual environment:**
   ```bash
   virtualenv -p python3 .
   source bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Build frontend assets:**
   ```bash
   ./build-frontend.sh
   ```

5. **Configure the application:**
   ```bash
   cp config.ini.example config.ini
   cp alembic.ini.example alembic.ini
   cp logging.ini.example logging.ini
   ```

6. **Set up database:**
   - Configure PostgreSQL connection in `config.ini`
   - Run the application once to create initial schema
   - Stamp alembic: `python -c "from alembic.config import Config; from alembic import command; alembic_cfg = Config('alembic.ini'); command.stamp(alembic_cfg, 'head')"`
   - For subsequent updates: `alembic upgrade head`

### Running the Application

**Development mode:**
```bash
python KerbalStuff/app.py
```

**Production mode (with gunicorn):**
```bash
gunicorn KerbalStuff.app:app -b 127.0.0.1:8000
```

**Running Celery worker (for emails and background tasks):**
```bash
celery -A KerbalStuff.celery:app worker --loglevel=info
```

### Running Tests

```bash
python -m pytest tests/
```

## Project Structure

### Main Directories

- **`KerbalStuff/`** - Main application package
  - `app.py` - Flask application entry point
  - `blueprints/` - Application blueprints (routes and views)
  - `objects.py` - Database models
  - `database.py` - Database configuration
  - `config.py` - Configuration management
  - `celery.py` - Celery task configuration

- **`templates/`** - Twig templates for all views
- **`frontend/`** - Frontend assets
  - `coffee/` - CoffeeScript source files
  - `styles/` - SCSS stylesheets
  - `static/` - Compiled assets (JS, CSS, images)
- **`tests/`** - Test suite
- **`alembic/`** - Database migrations

### Key Files

- **`config.ini.example`** - Configuration template
- **`requirements.txt`** - Main Python dependencies
- **`requirements-backend.txt`** - Backend-specific dependencies
- **`requirements-celery.txt`** - Celery worker dependencies
- **`requirements-prod.txt`**** - Production dependencies
- **`setup.py`** - Package configuration

## Development Workflow

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and modular
- Write comprehensive docstrings
- Include tests for new functionality

### Testing Approach

- Unit tests for logic
- Integration tests for API endpoints
- Functional tests for user flows
- Test database operations with SQLite in memory

### Build and Deployment

1. **Frontend build:**
   ```bash
   ./build-frontend.sh
   ```

2. **Database migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Deployment options:**
   - Docker (see Docker-related files)
   - Traditional server with uWSGI + nginx
   - Systemd service files provided in `systemd/`

### Contribution Guidelines

1. Fork the repository and create a feature branch
2. Make your changes with clear commit messages
3. Add tests for new functionality
4. Update documentation as needed
5. Submit a pull request with detailed description

## Key Concepts

### Domain-Specific Terminology

- **Mod**: A game modification (the core content type)
- **Publisher**: User or organization that creates mods
- **Game Version**: Supported versions of the game
- **List**: User-created collections of mods
- **Announcement**: Site-wide notifications

### Core Abstractions

- **User System**: Registration, authentication, profiles
- **Mod Management**: Upload, versioning, updates
- **GitHub Integration**: Automatic updates from GitHub repositories
- **Email System**: Registration confirmations, notifications

### Design Patterns

- **Blueprint Pattern**: Flask blueprints for organizing routes
- **Repository Pattern**: Database access layer
- **Task Queue Pattern**: Celery for background jobs
- **Template Inheritance**: Twig template hierarchy

## Common Tasks

### Creating a New Blueprint

1. Create a new file in `KerbalStuff/blueprints/`
2. Define routes and views
3. Register the blueprint in `app.py`

### Adding a Database Model

1. Define the model in `objects.py`
2. Create a migration: `alembic revision -m "message"`
3. Update the migration file
4. Run the migration: `alembic upgrade head`

### Adding Frontend Assets

1. Add CoffeeScript to `frontend/coffee/`
2. Add SCSS to `frontend/styles/`
3. Rebuild assets: `./build-frontend.sh`

### Creating an Admin Page

1. Add route to `KerbalStuff/blueprints/admin.py`
2. Create template in `templates/admin-*.html`
3. Add to admin navigation in template

## Troubleshooting

### Common Issues

**Database connection problems:**
- Check PostgreSQL service is running
- Verify connection string in `config.ini`
- Ensure user has proper permissions

**Frontend assets not loading:**
- Run `./build-frontend.sh`
- Check browser console for 404 errors
- Verify static files are in `frontend/static/`

**Celery tasks not running:**
- Check Redis service is running
- Verify Celery worker is started
- Check task queue configuration

**Email not sending:**
- Verify SMTP settings in `config.ini`
- Check Redis connection
- Ensure Celery worker is running

### Debugging Tips

- Enable debug mode in `config.ini`
- Use Flask's debug toolbar
- Check application logs
- Enable SQL query logging
- Use Python's pdb for interactive debugging

## References

### Official Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Project Resources

- [SpaceDock Website](https://spacedock.info)
- [GitHub Repository](https://github.com/KSP-SpaceDock/SpaceDock)
- [Development Guide Wiki](https://github.com/KSP-SpaceDock/SpaceDock/wiki/Development-Guide)
- [Infrastructure Wiki](https://github.com/KSP-SpaceDock/SpaceDock/wiki/Infrastructure)

### Configuration Files

- `config.ini` - Main application configuration
- `alembic.ini` - Database migration configuration
- `logging.ini` - Logging configuration
- `.env` - Environment variables

## Additional Notes

This CONTINUE.md file provides a comprehensive overview of the SpaceDock project. For more specific information about particular components, consider creating additional rules.md files in subdirectories.

Remember to:
1. Review and edit this file as needed
2. Commit it to your repository to share with your team
3. Continue will automatically load this file into context when working with the project


The development enviroment runs as docker containers on this machine.