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

"""INSPIRE migrator extension."""

from __future__ import print_function, absolute_import

import json
import os
import pkg_resources

from sqlalchemy import event

from invenio_collections.models import Collection
from invenio_db import db

from .cli import migrator


def load_collection_fixture():
    """Load collection fixture to database."""
    collections = json.loads(
        pkg_resources.resource_string(
            'inspirehep',
            os.path.join(
                'demosite',
                'data',
                'collection.json'
            )
        )
    )

    for collection in collections:
        c = Collection(name=collection['name'], dbquery=collection['dbquery'])
        db.session.add(c)
    db.session.commit()


class INSPIREMigrator(object):

    """INSPIRE migrator extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)
            self.register_signals()

    def init_app(self, app, **kwargs):
        """Initialize application object."""
        app.cli.add_command(migrator)
        self.init_config(app.config)
        # Save reference to self on object
        app.extensions['inspire-migrator'] = self

    def init_config(self, config):
        """Initialize configuration."""
        config.setdefault(
            'CFG_INSPIRE_LEGACY_BASEURL',
            'http://inspireheptest.cern.ch'
        )

    def register_signals(self):
        """Register signals."""
        @event.listens_for(Collection.__table__, 'after_create')
        def receive_after_create(target, connection, **kw):
            load_collection_fixture()

__all__ = ('INSPIREMigrator',)
