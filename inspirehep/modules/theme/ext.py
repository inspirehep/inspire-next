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

"""Invenio standard theme."""

from __future__ import absolute_import, print_function


from flask_breadcrumbs import Breadcrumbs
from flask_menu import Menu

from .views import blueprint


class INSPIRETheme(object):
    """Invenio theme extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        self.menu_ext = Menu()
        self.menu = None
        self.breadcrumbs = Breadcrumbs()

        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, assets=None, **kwargs):
        """Initialize application object."""
        self.init_config(app.config)

        # Initialize extensions
        self.menu_ext.init_app(app)
        self.menu = app.extensions['menu']
        self.breadcrumbs.init_app(app)

        app.register_blueprint(blueprint)

        # Register errors handlers.
        # app.register_error_handler(401, unauthorized)
        # app.register_error_handler(403, insufficient_permissions)
        # app.register_error_handler(404, page_not_found)
        # app.register_error_handler(500, internal_error)

        # Save reference to self on object
        app.extensions['inspire-theme'] = self

    def init_config(self, config):
        """Initialize configuration."""
        from .bundles import js
        # Set JS bundles to exclude for purpose of avoiding double jQuery etc.
        # when other modules are building their JS bundles.
        config.setdefault("THEME_BASE_BUNDLES_EXCLUDE_JS", [js])
        config.setdefault("BASE_TEMPLATE", "inspirehep_theme/page.html")
