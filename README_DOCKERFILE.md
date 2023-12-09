# How to use the Dockerfile

It should be assumed that all commands should be run from the project root, unless otherwise noted.
Additionally, depending on your platform and how you've setup Docker, `docker` commands might need to be run as the `root` user or prefaced with `sudo` to work properly.

## Quickstart

```sh
./start-server.sh
```

Admin Credentials: admin:development

User Credentials: user:development

## Install Docker

See <https://www.docker.com/> for instructions on installing Docker for your platform.

## Configure, Build, and Run

The launch script will automatically copy the `config.ini.example`, `alembic.ini.example` and `logging.ini.example` to `config.ini`, `alembic.ini` and `logging.ini`, respectively.
If you wish to provide your own, copy them like below and edit as you will.

```sh
cp config.ini.example config.ini && cp alembic.ini.example alembic.ini && cp logging.ini.example logging.ini
```

To create all the required containers and startup SpaceDock, run

```sh
./start-server.sh
```

This will automatically link `./` to `/opt/spacedock` in the backend container, as well as `./spacedock-db` into the database container and `./storage` into the frontend container.
This means that changes you make locally to files in your project folder will be instantly synced to and reflected in the container (however CSS and JS files need to be rebuilt before the changes take effect).
This will also forward port 5080 of the nginx container to port 5080 of your host, so you'll be able to browse to your local server.

The following containers will be started:

| docker-compose service name | container name | function |
| --------------------------- | -------------- | -------- |
| backend              | spacedock_backend_1   | Flask development server |
| db                   | spacedock_db_1        | PostgreSQL database |
| redis                | spacedock_redis_1     | Redis in-memory Key-Value store (required for Celery) |
| frontend             | spacedock_frontend_1  | NGINX frontend acting as proxy to the backend and serving static files |
| adminer              | spacedock_adminer_1   | Database management UI for development and debugging |

To interact with a container using the `docker` command, you need to use the container name.
To interact using `docker-compose`, you need to use the service name and be in the repository directory or any subdirectory.

## Connecting

If you are on macOS or another environment that requires the use of docker-machine, then you must connect to the local server via that docker machine rather than localhost.

To find out the correct IP to use in your browser, use `docker-machine ip`. You can then browse to port 5080 of that IP and all should be well.

There are two default accounts, an admin and a regular user:
Admin Credentials: admin:development
User Credentials: user:development

## Starting and Stopping

If you want to stop your container without losing any data, you can simply do `docker-compose stop`.
Then, to start it back up, do `docker-compose up`.

## Odd and Ends

```sh
docker-compose exec backend /bin/bash # Start a bash shell in the backend container
```
