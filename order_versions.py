from SpaceDock.database import db
from SpaceDock.objects import ModVersion, Mod

for m in Mod.query.all():
    if len(m.versions) == 0:
        continue
    versions = sorted(m.versions, key=lambda v: v.created)
    m.default_version_id = versions[-1].id
    print("Set version " + versions[-1].friendly_version + " as the default for " + m.name)
    for i, v in enumerate(versions):
        print("Setting sort order " + str(i) + " on " + m.name + " " + v.friendly_version)
        v.sort_index = i
    db.commit()
