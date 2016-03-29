# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
