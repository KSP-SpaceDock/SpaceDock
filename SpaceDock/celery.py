import smtplib
from celery import Celery
from email.mime.text import MIMEText
from SpaceDock.config import _cfg, _cfgi, _cfgb
import redis
import requests
import time
import json

app = Celery("tasks", broker=_cfg("redis-connection"))
donation_cache = redis.Redis(host=_cfg('patreon-host'), port=_cfg('patreon-port'), db=_cfg('patreon-db'))

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

@app.task
def send_mail(sender, recipients, subject, message, important=False):
    if _cfg("smtp-host") == "":
        return
    smtp = smtplib.SMTP(host=_cfg("smtp-host"), port=_cfgi("smtp-port"))
    if _cfgb("smtp-tls"):
        smtp.starttls()
    if _cfg("smtp-user") != "":
        smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
    message = MIMEText(message)
    if important:
        message['X-MC-Important'] = "true"
    message['X-MC-PreserveRecipients'] = "false"
    message['Subject'] = subject
    message['From'] = sender
    if len(recipients) > 1:
        message['Precedence'] = 'bulk'
    for group in chunks(recipients, 100):
        if len(group) > 1:
            message['To'] = "undisclosed-recipients:;"
        else:
            message['To'] = ";".join(group)
        print("Sending email from {} to {} recipients".format(sender, len(group)))
        smtp.sendmail(sender, group, message.as_string())
    smtp.quit()

@app.task
def update_patreon():
    donation_cache.set('patreon_update_time', time.time())
    if _cfg('patreon_user_id') != '' and _cfg('patreon_campaign') != '':
        r = requests.get("https://api.patreon.com/user/" + _cfg('patreon_user_id'))
        if r.status_code == 200:
            patreon = json.loads(r.text)
            for linked_data in patreon['linked']:
                if 'creation_name' in linked_data and 'pledge_sum' in linked_data:
                    if linked_data['creation_name'] == _cfg('patreon_campaign'):
                        donation_cache.set('patreon_donation_amount', linked_data['pledge_sum'])
