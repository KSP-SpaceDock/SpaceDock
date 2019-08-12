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
            site_logger.warning('Repository is dirty, cannot pull changes')
            return
        origin = repo.remote('origin')
        if not origin.exists():
            site_logger.error('No "origin" remote in the repository')
            return
        old_hash = repo.head.object.hexsha
        origin.pull(branch)
        if old_hash == repo.head.object.hexsha:
            site_logger.info('Working tree is already up to date')
            if not _cfg('hook_update_same_version'):
                return
        else:
            site_logger.info('Pulled latest changes from origin/%s', branch)
        # run restart command in a subprocess to daemonize it from there
        # and avoid its killing by restart process
        from billiard import Process
        p = Process(target=_restart_subprocess,
                    args=(working_directory, restart_command))
        p.start()
        p.join()
    except Exception:
        site_logger.exception('Unable to update from github')


# to debug this:
# * add PTRACE capability to celery container via docker-compose.yaml
#   celery:
#     image: spacedock_celery
#     build:
#       context: ./
#       target: celery
#     user: spacedock
#     cap_add:
#       - SYS_PTRACE
# * install strace to corresponding container in Dockerfile:
#     FROM backend-dev as celery
#     ADD requirements-celery.txt ./
#     RUN pip3 install -r requirements-celery.txt
#     RUN apt-get update && apt-get install strace
# * when the service is running, enter this container:
#     > docker exec -u root -it $(docker ps -q -f "name=spacedock_celery") bash
# * run strace as follows:
#     > strace -tt -f -p $(pgrep celery | head -n 2 | tail -n 1) -s 10000 -o celery/strace.log -e trace='!close,read,mmap,munmap'
# * explore the logs outside of the container in <SpaceDock>/celery/strace.log

def _restart_subprocess(working_directory, restart_command):
    """
    Run restart_command in a daemonized subprocess to avoid killing it
    by systemd when the restart process begin.

    In a docker container there's no init, so no one will reap
    the two processes that entering DaemonContext will spawn.
    They become zombies. So this code is strictly specific to the
    live production systems on which alpha/beta/prod are running.
    """
    import daemon
    import signal
    import syslog
    import sys
    import os
    # have to set std streams to devnull, because in celery they're replaced
    # with the LoggingProxy that doesn't have fileno method
    sys.stdin = sys.stdout = sys.stderr = open(os.devnull, 'w')
    try:
        def _signal_handler(sig, _frame):
            syslog.syslog(syslog.LOG_INFO, f'[celery._restart_subprocess] ignoring signal: {sig}')

        with daemon.DaemonContext(working_directory=working_directory,
                                  detach_process=True,
                                  umask=0o002,
                                  signal_map={signal.SIGQUIT: _signal_handler,
                                              signal.SIGTERM: _signal_handler,
                                              signal.SIGHUP: _signal_handler,
                                              signal.SIGABRT: _signal_handler}
                                  ):
            import logging
            from logging.config import fileConfig
            # recreate handlers to reopen corresponding output streams
            fileConfig('logging.ini')
            logger = logging.getLogger('system')
            try:
                logger.info('Starting: %s', restart_command)
                from subprocess import check_call
                check_call(restart_command.split())
                logger.info('Command has finished: %s', restart_command)
            except Exception:
                logger.exception('Error while running: %s', restart_command)
    except Exception:
        site_logger.exception('Unable to start detached process to run: %s', restart_command)
