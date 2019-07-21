from alembic.config import Config
from alembic import command
from KerbalStuff.objects import *
from KerbalStuff.database import db

# Make sure tables are created
alembic_cfg = Config("alembic.ini")
command.stamp(alembic_cfg, "head")
command.upgrade(alembic_cfg, "head")

# Create admin user if doesn't exist
if not User.query.filter(User.username.ilike("admin")).first():
    admin = User("admin", "admin@example.com", "development")
    admin.admin = True
    admin.public = True
    admin.confirmation = None
    db.add(admin)
    db.commit()

# Create normal user if doesn't exist
if not User.query.filter(User.username.ilike("user")).first():
    user = User("user", "user@example.com", "development")
    user.public = True
    user.confirmation = None
    db.add(user)
    db.commit()

if not Publisher.query.first():
    pub = Publisher("Squad")
    db.add(pub)
    db.commit()

if not Game.query.first():
    game = Game("Kerbal Space Program", 1, "kerbal-space-program")
    game.active = True
    db.add(game)
    db.commit()

if not GameVersion.query.first():
    gameversion = GameVersion('1.0', 1)
    db.add(gameversion)
    db.commit()
