# SpaceDock Architecture

This document provides an overview of the SpaceDock architecture, including the technology stack, component interactions, and design patterns used in the project.

## Technology Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Language**: Python 3.8+
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Authorization**: Role-based access control
- **Task Queue**: Celery with Redis
- **Caching**: Redis

### Frontend
- **Language**: CoffeeScript (compiled to JavaScript)
- **Styling**: SCSS (compiled to CSS)
- **Templates**: Twig
- **Build System**: Webpack (via npm scripts)
- **Package Manager**: npm

### Infrastructure
- **Web Server**: Nginx
- **Application Server**: uWSGI
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Monitoring**: Prometheus, Grafana
- **Error Tracking**: Sentry
- **CI/CD**: GitHub Actions

## Component Architecture

### High-Level Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                Client (Browser)                                │
└───────────────────────────────────────────────────────────────────────────────┘
                                      ↑ ↓ HTTP/HTTPS
┌───────────────────────────────────────────────────────────────────────────────┐
│                                Nginx (Reverse Proxy)                          │
└───────────────────────────────────────────────────────────────────────────────┘
                                      ↑ ↓ HTTP
┌───────────────────────────────────────────────────────────────────────────────┐
│                                uWSGI (Application Server)                    │
└───────────────────────────────────────────────────────────────────────────────┘
                                      ↑ ↓ Python
┌───────────────────────────────────────────────────────────────────────────────┐
│                                Flask Application                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐    │
│  │   Blueprints    │    │   Database     │    │   Celery Tasks     │    │
│  │  (Routes/Views) │    │   (SQLAlchemy)  │    │   (Background Jobs) │    │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────┘
                                      ↑ ↓ SQL/Redis
┌───────────────────────────────────────────────────────────────────────────────┐
│                                PostgreSQL                                 │
└───────────────────────────────────────────────────────────────────────────────┘
                                      ↑ ↓ Redis
┌───────────────────────────────────────────────────────────────────────────────┐
│                                Redis (Cache/Queue)                           │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Flask Blueprints

SpaceDock uses Flask blueprints to organize routes and views into logical components:

- **accounts.py**: User authentication and account management
- **admin.py**: Administrative interfaces and tools
- **anonymous.py**: Routes for non-authenticated users
- **api.py**: RESTful API endpoints
- **blog.py**: Blog and announcement system
- **lists.py**: User-created mod collections
- **mods.py**: Mod management and display
- **profile.py**: User profile pages

### Database Schema

The database follows a relational model with key entities:

- **User**: Represents website users with authentication credentials
- **Mod**: Game modifications with metadata and versions
- **ModVersion**: Different versions of a mod with download links
- **GameVersion**: Supported versions of Kerbal Space Program
- **List**: User-created collections of mods
- **Download**: Tracking of mod downloads
- **Follow**: User relationships (following mods or users)

### Frontend Structure

The frontend is organized into reusable components:

```
frontend/
├── coffee/
│   ├── app.coffee          # Main application
│   ├── components/         # Reusable UI components
│   │   ├── mod_card.coffee # Mod card component
│   │   ├── navbar.coffee   # Navigation bar
│   │   └── ...             # Other components
│   ├── pages/              # Page-specific logic
│   │   ├── mods.coffee     # Mods page logic
│   │   └── ...             # Other pages
│   └── utils/              # Utility functions
│       ├── api.coffee      # API helper functions
│       └── ...             # Other utilities
├── styles/
│   ├── main.scss          # Main stylesheet
│   ├── components/         # Component styles
│   │   ├── mod_card.scss   # Mod card styles
│   │   └── ...             # Other component styles
│   ├── pages/              # Page-specific styles
│   │   ├── mods.scss       # Mods page styles
│   │   └── ...             # Other page styles
│   └── utils/              # Mixins and variables
│       ├── _variables.scss # SCSS variables
│       └── _mixins.scss    # SCSS mixins
└── static/                 # Compiled assets
    ├── css/                # Compiled CSS
    ├── js/                 # Compiled JavaScript
    └── images/             # Static assets
```

## Design Patterns

### Repository Pattern

The repository pattern is used to abstract database operations:

```python
class ModRepository:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def get_by_id(self, mod_id):
        return self.db_session.query(Mod).filter(Mod.id == mod_id).first()
    
    def create(self, name, description, author):
        mod = Mod(name=name, description=description, author=author)
        self.db_session.add(mod)
        self.db_session.commit()
        return mod
```

### Service Layer

A service layer separates business logic from routes:

```python
class ModService:
    def __init__(self, mod_repository):
        self.mod_repository = mod_repository
    
    def create_mod(self, user, mod_data):
        # Validate input
        if not mod_data.get('name'):
            raise ValueError("Mod name is required")
        
        # Create mod
        mod = self.mod_repository.create(
            name=mod_data['name'],
            description=mod_data.get('description', ''),
            author=user
        )
        
        # Additional business logic
        self._notify_admins(mod)
        
        return mod
    
    def _notify_admins(self, mod):
        # Notify admins of new mod
        pass
```

### Factory Pattern

Factories are used to create instances of classes:

```python
class ModFactory:
    @staticmethod
    def create_from_github(github_data):
        return Mod(
            name=github_data['name'],
            description=github_data.get('description', ''),
            author=User.query.filter_by(username=github_data['owner']).first()
        )
```

## Data Flow

### Mod Creation Flow

1. User submits mod creation form
2. Flask route receives POST request
3. Service layer validates input and creates mod
4. Repository saves mod to database
5. Celery task generates mod thumbnail
6. Response is sent back to user

### Mod Download Flow

1. User clicks download button
2. Flask route receives GET request
3. Service layer increments download counter
4. Repository updates database
5. Redirect to download URL
6. Celery task logs download event

## Caching Strategy
