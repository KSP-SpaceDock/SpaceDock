from KerbalStuff.objects import *
from KerbalStuff.database import *

for game in Game.query:
    game.active = True
    db.commit()

for mod in Mod.query:
    if mod.default_version().ksp_version == "for WiiU":
        mod.game = Game.query.filter(Game.name == "Super Smash Bros. for Wii U").first()
        db.commit()
