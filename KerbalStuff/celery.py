from celery import Celery

from .config import _cfg, _cfgi, _cfgb

app = Celery("tasks", broker=_cfg("redis-connection"))


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


@app.task
def send_mail(sender, recipients, subject, message, important=False):
    if not _cfg("smtp-host"):
        return
    import smtplib
    from email.mime.text import MIMEText
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
def notify_ckan(mod_id, event_type):
    if not _cfg("notify-url"):
        return
    import requests
    send_data = {'mod_id': mod_id, 'event_type': event_type}
    requests.post(_cfg("notify-url"), send_data)


@app.task
def update_from_github(working_directory):
    print('Updating the site from github...')
    import os
    cwdir = os.getcwd()
    try:
        # pull new sources from git
        import subprocess
        os.chdir(working_directory)
        subprocess.call(["git", "pull", "origin", _cfg("hook_branch")])
        # run restart command in daemonized process to avoid its killing by restart process
        import daemon
        with daemon.DaemonContext(working_directory=working_directory):
            subprocess.call(_cfg("restart_command").split())
    except Exception as e:
        print(f'Unable to update service from github: {e!s}')
    else:
        print('Done')
    finally:
        os.chdir(cwdir)
