# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE
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
# along with INSPIRE; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Warnings extension that removes deprecation warnings.

Invenio-Base enables deprecation warnings and this extension removes
this setting unless ``DEBUG_SHOW_DEPRECATION_WARNINGS`` is set to True.
"""

from __future__ import absolute_import


class INSPIREWarnings(object):
    """INSPIREWarnings extension implementation."""

    def __init__(self, app=None):
        """Initialize extension."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize a Flask application."""
        app.config.setdefault("DEBUG_SHOW_DEPRECATION_WARNINGS",
                              False)

        if not app.config['DEBUG_SHOW_DEPRECATION_WARNINGS']:
            import warnings
            warnings.filterwarnings(
                'ignore',
                category=DeprecationWarning
            )
        app.extensions["inspire-warnings"] = self


__all__ = ("INSPIREWarnings", )
