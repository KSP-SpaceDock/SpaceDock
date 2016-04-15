from KerbalStuff.objects import *
from KerbalStuff.database import *


for mod in Mod.query:
    mod.ckan = False
    db.commit()
