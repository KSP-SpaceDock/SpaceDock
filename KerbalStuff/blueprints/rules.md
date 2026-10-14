# SpaceDock Blueprints Documentation

This file provides detailed documentation about the Flask blueprints architecture in SpaceDock.

## Blueprint Structure

SpaceDock uses Flask blueprints to organize routes and views. Each blueprint represents a logical component of the application.

### Available Blueprints

- **accounts.py** - User authentication and account management
- **admin.py** - Administrative interfaces and tools
- **anonymous.py** - Routes for non-authenticated users
- **api.py** - RESTful API endpoints
- **blog.py** - Blog and announcement system
- **lists.py** - User-created mod collections
- **mods.py** - Mod management and display
- **profile.py** - User profile pages

## Creating a New Blueprint

To create a new blueprint:

1. Create a new file in `KerbalStuff/blueprints/` with your feature name
2. Define routes using the `@blueprint.route()` decorator
3. Register the blueprint in `KerbalStuff/app.py`

### Example Blueprint Structure

```python
from flask import Blueprint, render_template

# Create blueprint instance
my_feature = Blueprint('my_feature', __name__)

# Define routes
@my_feature.route('/my-feature')
def index():
    return render_template('my_feature/index.html')

@my_feature.route('/my-feature/<int:item_id>')
def show(item_id):
    return render_template('my_feature/show.html', item_id=item_id)

# Register in app.py
app.register_blueprint(my_feature)
```

## Blueprint Best Practices

1. **Route Organization**: Group related routes together
2. **Template Structure**: Use consistent template naming (blueprint_name/view.html)
3. **Error Handling**: Implement consistent error handling patterns
4. **Dependency Injection**: Use Flask's dependency injection system
5. **Documentation**: Add docstrings to explain route purposes

## Common Blueprint Patterns

### API Endpoints
```python
from .common import json_output

@api.route('/api/mods')
@json_output
def get_mods():
    # Return JSON data
    return {'mods': Mod.query.all()}
```

### Protected Routes
```python
from flask_login import login_required

@profiles.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
```

### Template Rendering
```python
@blog.route('/blog')
def blog_index():
    posts = BlogPost.query.order_by(BlogPost.published.desc()).all()
    return render_template('blog_index.html', posts=posts)
```

## Blueprint Integration

All blueprints are integrated in `KerbalStuff/app.py`:

```python
from .blueprints.accounts import accounts
from .blueprints.admin import admin
# ... other imports

app.register_blueprint(profiles)
app.register_blueprint(accounts)
app.register_blueprint(anonymous)
app.register_blueprint(blog)
app.register_blueprint(admin)
app.register_blueprint(mods)
app.register_blueprint(lists)
app.register_blueprint(api)
```

## Blueprint-Specific Configuration

Some blueprints may require additional configuration:

```python
# Example: API blueprint with URL prefix
api = Blueprint('api', __name__, url_prefix='/api')
```

## Testing Blueprints

When testing blueprints, use Flask's test client:

```python
def test_mod_routes(client):
    # Test GET request
    response = client.get('/mods')
    assert response.status_code == 200

    # Test POST request
    response = client.post('/mods', data={'name': 'Test Mod'})
    assert response.status_code == 302  # Redirect after creation
```

For more information about Flask blueprints, see the [Flask Blueprint Documentation](https://flask.palletsprojects.com/en/1.1.x/blueprints/).
"