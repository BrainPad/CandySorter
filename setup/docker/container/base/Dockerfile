FROM ubuntu:18.04

RUN set -ex \
  && sed -i -e "s%http://archive.ubuntu.com/ubuntu/%http://no.archive.ubuntu.com/ubuntu/%g" /etc/apt/sources.list \
  && apt-get update && apt-get install -y \
    libblas3 \
    liblapack3 \
    nginx \
    python3-dev \
    python3-pip \
    supervisor \
    vim \
  && rm /etc/nginx/sites-enabled/default \
  && pip3 install --upgrade pip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
