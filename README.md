# SpaceDock

Website engine for Kerbal Space Program mods.

https://spacedock.info

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md)

## Installation

This describes a bare-metal setup. For a local development setup using Docker, see https://github.com/KSP-SpaceDock/SpaceDock/wiki/Development-Guide#running-with-docker.

Quick overview:

1. Install and set up the dependencies
2. Clone SpaceDock repository
3. Activate the virtualenv
4. Install pip requirements
5. Build frontend
6. Configure SpaceDock
7. SQL
8. Site configuration

**Install the dependencies**

You'll need these things:
(Names taken from Ubuntu's package repository)

* python3, python3-dev for uwsgi, python3-pip, python3-virtualenv
* nodejs, npm
* postgresql (or postgresql-client if the database is on another server)
* redis-tools

Use the packages your OS provides, or build them from source.
For an up to date NodeJS distribution, see https://nodejs.org/en/download/current/
and https://github.com/nodesource/distributions/blob/master/README.md

**Set up services**

Do a quick sanity check on all of those things.

    $ python3 --version
      Python 3.8.10
    $ node --version
      v16.6.1
    $ npm --version
      7.20.3
    $ pip --version
      pip 21.2.3
    $ virtualenv --version
      virtualenv 20.0.17
    $ psql --version
      psql (PostgreSQL) 12.7 (Ubuntu 12.7-0ubuntu0.20.04.1)
    $ redis-cli --version
      redis-cli 5.0.7

YMMV if you use versions that differ from these.

Prepare a connection string that looks like this when you're done, prepare PostgreSQL accordingly:

    postgresql://username:password@hostname:port/database

The connection string for localhost can look like this:

    postgresql://postgres@localhost/spacedock

SpaceDock needs to be able to create/alter/insert/update/delete in the database
you give it.

You also need to start up Redis on the default port if you want to send emails.

**Clone SpaceDock**

Find a place you want the code to live.

    $ git clone git://github.com/KSP-SpaceDock/SpaceDock.git
    $ cd SpaceDock

**Activate virtualenv**

    $ virtualenv -p python3 .
    $ source bin/activate

If you are on a system where `python3` is not the name of your
Python executable, add `--python=/path/to/python3` to the virtualenv command to fix that.

**pip requirements**

If you use systemd/spacedock.target or Docker, this will be done automatically for you.

    $ pip install -r requirements.txt

**Frontend**

    $ ./build-frontend.sh

**Configure SpaceDock**

    $ cp config.ini.example config.ini
    $ cp alembic.ini.example alembic.ini
    $ cp logging.ini.example logging.ini

Edit config.ini and alembic.ini to your liking.

**Postgres Configuration**

Depending on your environment, you may need to tell postgres to trust localhost connections. This setting is in the pg_hba.conf file, usually located in /etc/postgresql/[version]/main/.
An example of what the config should look like:

    local   all    all                    trust
    host    all    all    127.0.0.1/32    trust
    host    all    all    ::1/128         trust    #may or may not be needed for IPv6 aware installs

**Site Configuration**

What you do from here depends on your site-specific configuration. If you just
want to run the site for development, you can source the virtualenv and run

    python app.py

To run it in production, you probably want to use gunicorn behind an nginx proxy.
There's a sample nginx config in the configs/ directory here, but you'll probably
want to tweak it to suit your needs. Here's how you can run gunicorn, put this in
your init scripts:

    /path/to/SpaceDock/bin/gunicorn app:app -b 127.0.0.1:8000

The `-b` parameter specifies an endpoint to use. You probably want to bind this to
localhost and proxy through from nginx. I'd also suggest blocking the port you
choose from external access. It's not that gunicorn is *bad*, it's just that nginx
is better.

To get an admin user you have to register a user first and then run this (replace &lt;username&gt; with your username):

	source bin/activate
	python

	from KerbalStuff.objects import *
	from KerbalStuff.database import db
	u = User.query.filter(User.username == "<username>").first()
	u.admin = True
	u.confirmation = None
	db.commit()


When running in a production environment, run `python app.py` at least once and
then read the SQL stuff below before you let it go for good.

## Emails

If you want to send emails (like registration confirmation, mod updates, etc),
you need to have redis running and then start the KerbalStuff mailer daemon.
You can run it like so:

    celery -A KerbalStuff.celery:app worker --loglevel=info

Of course, this only works if you've filled out the smtp options in `config.ini`
and you have sourced the virtualenv.

## SQL Stuff

We use alembic for schema migrations between versions. The first time you run the
application, the schema will be created. However, you need to tell alembic about
it. Run the application at least once, then:

    $ cd /path/to/SpaceDock/
    $ source bin/activate
    $ python
    >>> from alembic.config import Config
    >>> from alembic import command
    >>> alembic_cfg = Config("alembic.ini")
    >>> command.stamp(alembic_cfg, "head")
    >>> exit()

Congrats, you've got a schema in place. Run `alembic upgrade head` after pulling
the code to update your schema to the latest version. Do this before you restart
the site.
