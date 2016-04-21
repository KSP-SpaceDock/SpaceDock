import requests
import os
import sys
import subprocess
from werkzeug.utils import secure_filename
from SpaceDock.objects import Mod
from SpaceDock.config import _cfg
from SpaceDock.database import db

def download_bg(url, path):
    sys.stdout.write("\rDownloading {0}...".format(path))
    subprocess.call(['wget', '--output-document=' + path, url])
    sys.stdout.write("\n")

total = Mod.query.count()
for index, mod in enumerate(Mod.query.all()):
    if mod.background:
        print("Handling {} ({} of {})".format(mod.name, index + 1, total))

        filetype = os.path.splitext(os.path.basename(mod.background))[1]
        filename = secure_filename(mod.name) + filetype
        base_path = os.path.join(secure_filename(mod.user.username) + '_' + str(mod.user.id), secure_filename(mod.name))
        full_path = os.path.join(_cfg('storage'), base_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        path = os.path.join(full_path, filename)

        download_bg('https://vox.mediacru.sh/' + mod.background, path)
        mod.background = os.path.join(base_path, filename)
        db.commit()
