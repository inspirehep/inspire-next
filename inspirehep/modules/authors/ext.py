# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""INSPIRE module to manage authors."""

from __future__ import absolute_import, print_function

from .views import blueprint

from . import config


class INSPIREAuthors(object):
    """INSPIRE authors extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, assets=None, **kwargs):
        """Initialize application object."""
        self.init_config(app)
        app.register_blueprint(blueprint)
        app.extensions['inspire-authors'] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('AUTHORS_'):
                app.config.setdefault(k, getattr(config, k))

        # URL used to prefill author update form
        app.config.setdefault("AUTHORS_UPDATE_BASE_URL",
                              app.config["SERVER_NAME"])
