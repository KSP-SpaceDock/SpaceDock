from KerbalStuff.objects import *
from KerbalStuff.database import *

for modv in ModVersion.query:
    modv.gameversion = GameVersion.query.filter(GameVersion.id==modv.mod.game.version[0].id).first()
    print(modv.gameversion)
    db.add(modv)

db.commit()
