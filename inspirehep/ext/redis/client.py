# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


""" Extension for Redis client """

from flask import current_app


class Redis(object):
    """Redis extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        self._clients = {}

        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, redis=None):
        # Configure redis client.
        self._clients[app] = redis
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['redis.client'] = self

    @classmethod
    def _client_builder(cls, app):
        """Default Redis client builder."""
        from werkzeug.contrib.cache import RedisCache

        host = app.config.get('CACHE_REDIS_URL', 'localhost')
        prefix = app.config.get('CFG_DATABASE_NAME', '') + '-redis::'

        return RedisCache(host, key_prefix=prefix, default_timeout=0)

    @property
    def client(self):
        """Return client for current application."""

        app = current_app._get_current_object()
        client = self._clients.get(app)
        if client is None:
            client = self._clients[app] = self.__class__._client_builder(app)
        return client


def setup_app(app):
    redis = Redis()
    redis.init_app(app)
