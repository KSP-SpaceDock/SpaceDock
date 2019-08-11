from celery import Celery

from .config import _cfg, _cfgi, _cfgb, site_logger

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
        site_logger.info("Sending email from %s to %s recipients", sender, len(group))
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
def update_from_github(working_directory, branch, restart_command):
    site_logger.info('Updating the site from github at: %s', working_directory)
    try:
        # pull new sources from git
        from git import Repo, GitError
        try:
            repo = Repo(working_directory)
            if repo.bare:
                raise GitError()
        except GitError:
            site_logger.warning('No git repository at: %s', working_directory)
            return
        if repo.is_dirty():
            site_logger.info('Repository is dirty, cannot pull changes')
            return
        origin = repo.remote('origin')
        if not origin.exists():
            site_logger.info('No "origin" remote in the repository')
            return
        origin.pull(branch)
        # run restart command in daemonized process to avoid its killing by restart process
        import daemon
        with daemon.DaemonContext(working_directory=working_directory,
                                  detach_process=True):
            from subprocess import check_call, CalledProcessError
            site_logger.info('Running restart command: %s', restart_command)
            try:
                check_call(restart_command.split())
            except Exception:
                site_logger.exception('Failed to restart the service')
    except Exception:
        site_logger.exception('Unable to update from github')
