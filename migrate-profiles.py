import requests
import os
import sys
import subprocess
from werkzeug.utils import secure_filename
from SpaceDock.objects import User
from SpaceDock.config import _cfg
from SpaceDock.database import db

def download_bg(url, path):
    sys.stdout.write("\rDownloading {0}...".format(path))
    subprocess.call(['wget', '--output-document=' + path, url])
    sys.stdout.write("\n")

total = User.query.count()
for index, user in enumerate(User.query.all()):
    if user.backgroundMedia:
        print("Handling {} ({} of {})".format(user.username, index + 1, total))

        filetype = os.path.splitext(os.path.basename(user.backgroundMedia))[1]
        filename = secure_filename(user.username) + filetype
        base_path = os.path.join(secure_filename(user.username) + '_' + str(user.id))
        full_path = os.path.join(_cfg('storage'), base_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        path = os.path.join(full_path, filename)

        download_bg('https://vox.mediacru.sh/' + user.backgroundMedia, path)
        user.backgroundMedia = os.path.join(base_path, filename)
        db.commit()
