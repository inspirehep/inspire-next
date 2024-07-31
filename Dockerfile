# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2019 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


# Modified and simplified version of https://github.com/inspirehep/inspire-docker
# to build an imagine to run in https://github.com/inspirehep/inspirehep

FROM fedora:40

RUN dnf update -y && \
    dnf install -y ImageMagick \
    transfig \
    file \
    firefox \
    gcc \
    gcc-c++ \
    git \
    kstart \
    libffi-devel \
    libxml2-devel \
    libxslt-devel \
    mailcap \
    xrootd-client-devel \
    openssl-devel \
    poppler-utils \
    postgresql \
    postgresql-libs \
    postgresql-devel \
    python2.7 \
    wget \
    Xvfb \
    xrootd \
    && dnf clean all


ENV NODE_VERSION 6.17.1
RUN mkdir /usr/local/nvm
ENV NVM_DIR /usr/local/nvm

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash

# install node and npm LTS
RUN source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN npm install -g \
    node-sass@3.8.0 \
    clean-css@^3.4.24 \
    requirejs \
    uglify-js

WORKDIR /code

RUN wget https://bootstrap.pypa.io/pip/2.7/get-pip.py && \
    python2 get-pip.py && \
    rm get-pip.py

COPY . .

RUN python2.7 -m pip install poetry==1.1.15 && \
    python2.7 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org  --trusted-host files.pythonhosted.org --ignore-installed --no-cache-dir --upgrade pip==20.3.4 && \
    python2.7 -m pip install --no-cache-dir --upgrade setuptools && \
    python2.7 -m pip install --no-cache-dir --upgrade wheel



RUN poetry config virtualenvs.create false && \
    poetry export --without-hashes -E all -E xrootd -f requirements.txt > requirements.poetry.txt
    
RUN python2.7 -m pip install --ignore-installed --requirement requirements.poetry.txt && \
    python2.7 -m pip install -e . && \
    python2.7 -m pip install git+https://github.com/inspirehep/xrootd-python.git && \
    python2.7 -m pip install --requirement requirements_docker.txt
    

WORKDIR /usr/var/inspirehep-instance/static

RUN inspirehep npm && \ 
    npm install && \
    inspirehep collect -v && \
    inspirehep assets build

WORKDIR /code
