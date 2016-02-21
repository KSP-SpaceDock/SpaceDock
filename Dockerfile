FROM ubuntu:14.04
MAINTAINER frikfry@gmail.com # Someone let me know an appropriate email for the project

# Needed to fix pip install of requirements due to strange char encoding issue.
ENV LC_CTYPE C.UTF-8
# Set this to suppress 'debconf: unable to initialize frontend' errors
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y curl
# This needs to be broken up because curl isn't available at the start and we need curl to install nodejs
RUN curl -sL https://deb.nodesource.com/setup | sudo bash -
# Don't need to apt-get update first because the script above does it for us.
RUN apt-get install -y supervisor libffi-dev nodejs vim postgresql-client libpq-dev python-pip python-dev python3-dev build-essential
RUN pip install --upgrade pip
RUN pip install virtualenv

# Make our directories
RUN mkdir -p /opt/spacedock
WORKDIR /opt/spacedock

# Install coffee-script
RUN npm install --global coffee-script

# Breaking up the installing of requirements like this so that it gets cached by docker
COPY requirements.txt /opt/spacedock/requirements.txt
RUN virtualenv --python=python3 --no-site-packages /venv/spacedock
RUN . /venv/spacedock/bin/activate && pip install -r requirements.txt

# Add everything else from the project root to the install dir.
COPY . /opt/spacedock

# Make a supervisord process for actually running the commands.
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run the app when the container starts.
CMD ["/usr/bin/supervisord"]
