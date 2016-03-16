FROM python:2.7

RUN apt-get update --fix-missing && \
    apt-get install -y \
      python-virtualenv \
      git \
      nodejs \
      npm \
      libpq-dev \
      build-essential \
      libxml2-dev \
      libxslt1-dev \
      libffi-dev \
      liblzma-dev && \
    ln -s /usr/bin/nodejs /usr/bin/node && \
    npm install -g \
      npm \
      node-sass \
      clean-css \
      requirejs \
      uglify-js

ADD . /code
WORKDIR /code

RUN virtualenv /tmpvenv && \
    . /tmpvenv/bin/activate && \
    pip install --upgrade pip-accel setuptools && \
    pip-accel install -r requirements.txt --pre && \
    rm -rf /code/* && \
    deactivate && \
    rm -rf /tmpvenv

ADD ./dockerfiles/docker_entrypoint.sh /docker_entrypoint.sh
ENTRYPOINT ["/docker_entrypoint.sh"]
CMD true
