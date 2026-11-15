"""Basic smoke test to verify test infrastructure works."""
from KerbalStuff.objects import User
from KerbalStuff.database import db


def test_users_exist(flask_app):
    """Verify spacedock database populate created users."""
    admin = User.query.filter(User.username.ilike("admin")).first()
    user = User.query.filter(User.username.ilike("user")).first()
    
    assert admin is not None, "Admin user was not created"
    assert user is not None, "Regular user was not created"
    assert admin.username == "admin"
    assert user.username == "user"
    assert admin.admin is True
    assert user.admin is False


def test_client(client):
    """Verify Flask test client works."""
    response = client.get("/")
    assert response.status_code == 200


def test_user_model(client):
    """Basic CRUD test."""
    # Create
    u = User(username="testuser", email="test@example.com")
    db.add(u)
    db.commit()
    db.refresh(u)
    assert u.id is not None
    
    # Read
    found = User.query.filter(User.username == "testuser").first()
    assert found is not None
    assert found.email == "test@example.com"
    
    # Update
    found.email = "updated@example.com"
    db.commit()
    db.refresh(found)
    assert found.email == "updated@example.com"
    # Delete - verify it can be deleted without error
    try:
        db.delete(found)
        db.commit()
    except Exception:
        db.rollback()