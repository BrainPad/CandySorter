FROM computas/fyc-base:latest

WORKDIR /opt/FindYourCandy
ARG container_dir="setup/docker/container/speech"

# Python libraries
COPY speech-app/requirements.txt speech-app/
COPY speech-app/requirements speech-app/requirements
RUN set -ex \
  && pip3 install -r speech-app/requirements.txt \
  && rm -rf ~/.cache/pip

# Nginx
#COPY ${container_dir}/nginx-speech.conf /etc/nginx/conf.d/

# uWSGI
#RUN set -ex && mkdir /etc/uwsgi /run/uwsgi
#COPY ${container_dir}/uwsgi-speech.ini /etc/uwsgi/

# Supervisor
# COPY ${container_dir}/supervisord-speech.conf /etc/supervisor/conf.d/

# Application
COPY speech-app speech-app
# RUN set -ex && ln -sf /proc/$$/fd/1 speech-app/logs/app.log

ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/FindYourCandy/data/credentials.json

EXPOSE 80
CMD ["python3","speech-app/run.py"]
