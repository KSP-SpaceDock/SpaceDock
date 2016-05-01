from alembic.config import Config
from alembic import command
from SpaceDock.objects import *
from SpaceDock.database import db

# Make sure tables are created
alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")
command.upgrade(alembic_cfg, "head")

# Create admin user if doesn't exist
if not User.query.filter(User.username.ilike("admin")).first():
    admin = User("admin", "admin@example.com", "development")
    admin.admin = True
    admin.confirmation = None
    db.add(admin)
    db.commit()

# Create normal user if doesn't exist
if not User.query.filter(User.username.ilike("user")).first():
    user = User("user", "user@example.com", "development")
    user.confirmation = None
    db.add(user)
    db.commit()
