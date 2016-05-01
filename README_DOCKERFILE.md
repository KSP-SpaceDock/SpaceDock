# How to use the Dockerfile
It should be assumed that all commands should be run from the project root, unless otherwise noted.
Additionally, depending on your platform and how you've setup Docker, ```docker``` commands might need to be run as the ```root``` user or prefaced with ```sudo``` to work properly.

## Quickstart
```
docker-compose up
```
Admin Credentials: admin:development

User Credentials: user:development

## Install Docker
See [https://www.docker.com/](docker.com) for instructions on installing Docker for your platform.

## Configure, Build, and Run
The dockerfile will automatically copy the config.ini.example and alembic.ini.example to config.ini and alembic.ini, respectfully. If you wish to provide your own, copy them like below and edit as you will.
```
cp config.ini.example config.ini && cp alembic.ini.example alembic.ini
```

To create all the required containers and startup spacedock, run
```
docker-compose up
```
This will automatically link ```your_project_root``` to ```/opt/spacedock``` on the container.
This means that changes you make locally to files in your project folder will be instantly synced to and reflected in the container.
This will also forward port 8000 of your docker contianer to port 8000 of your docker-machine, so you'll be able to browse to your local server.
Furthermore, this will also give the ```spacedock``` name to your container, which will make managing it easier.

You might run into a problem where changes to the Dockerfile are not reflected run you run ```docker-compose up```. This is expected. Run ```docker-compose rm -f && docker-compose build``` to force the containers to be rebuilt.

## Connecting
If you are on a mac or another environment that requires the use of docker-machine, then you must connect to the local server via that docker machine rather than localhost.

To find out the correct IP to use in your browser, use ```docker-machine ip```. You can then browser to port 5000 of that IP and all should be well.

There are two default accounts, an admin and a regular user:
Admin Credentials: admin:development
User Credentials: user:development

## Starting and Stopping
If you want to stop your container without losing any data, you can simply do ```docker-compose stop```.
Then, to start it back up, do ```docker-compose up```.

## Enabling Gunicorn
By default, the flask debug server is used to facilitate local development, as it handles serving static files better than gunicorn and has the Werkzeug debugger enabled. To enable using Gunicorn, which is recommended for a production environment, you should set the ```USE_GUNICORN``` environment variable when starting the docker container. Do so either in your user's .bashrc file or on the command-line like below.

```
USE_GUNICORN=true docker-compose up
```

## Odd and Ends
```
docker exec -i -t spacedock bash # Start a bash shell in the spacedock container
```
