from KerbalStuff.objects import *
from KerbalStuff.database import *

for game in Game.query:
    game.active = True
    db.commit()

for game in Game.query:
    if not game.name.startswith("Melee"):
        version = GameVersion(game.name, game.id)
        db.add(version)
        db.commit()
