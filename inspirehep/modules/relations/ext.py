# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from .cli import relations
from . import config

import os


class INSPIRERelations(object):
    """Inspire relations extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)

        self._client = kwargs.get('client')
        self._client_session = None
        self.app = app

    def init_app(self, app, **kwargs):
        """Flask application initialization.
        :param app: An instance of :class:`~flask.app.Flask`.
        """
        self.init_config(app)
        app.extensions['inspire-relations'] = self
        app.cli.add_command(relations)

    @staticmethod
    def init_config(app):
        """Initialize configuration.
        :param app: An instance of :class:`~flask.app.Flask`.
        """
        for k in dir(config):
            if k.startswith('RELATIONS_'):
                app.config.setdefault(k, getattr(config, k))

        app.config["RELATIONS_STORAGEDIR"] = os.environ.get(
            'RELATIONS_STORAGEDIR', os.path.join(
                app.instance_path, "relations", "storage"
            ))


    def _client_builder(self):
        from neo4j.v1 import GraphDatabase, basic_auth
        return GraphDatabase.driver(
            "bolt://" + self.app.config['RELATIONS_NEO4J_HOST'],
            auth=basic_auth(self.app.config['RELATIONS_NEO4J_USER'],
                            self.app.config['RELATIONS_NEO4J_PASSWORD'])
        )

    @property
    def graph_db(self):
        """Return client for current application."""
        if self._client is None:
            self._client = self._client_builder()
        return self._client


    @property
    def current_session(self):
        """Return current Neo4j session"""
        if self._client_session is None or not self._client_session.healthy:
            self._client_session = self.graph_db.session()
        return self._client_session
