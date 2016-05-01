from SpaceDock.objects import Game
from SpaceDock.database import db

for game in Game.query:
    game.background = "/content/" + game.short + ".jpg"
    db.commit()
