FROM python:3.8 as backend-dev
ENV PYTHONUNBUFFERED=1
RUN useradd -m -d /opt/spacedock -s /bin/bash spacedock
RUN pip3 install --upgrade pip setuptools wheel pip-licenses
WORKDIR /opt/spacedock
ADD requirements-backend.txt ./
RUN pip3 install -r requirements-backend.txt
ADD . ./
RUN pip3 install -v ./

FROM backend-dev as celery
ADD requirements-celery.txt ./
RUN pip3 install -r requirements-celery.txt

FROM backend-dev as backend-prod
ADD requirements-prod.txt ./
RUN pip3 install -r requirements-prod.txt
