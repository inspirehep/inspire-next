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

"""Extension that suppresses warnings.

By default Invenio-Base enables deprecation warnings. This extension
disables them, unless ``DEBUG_SHOW_DEPRECATION_WARNINGS`` is ``True``.
"""

from __future__ import absolute_import, division, print_function

import warnings


class INSPIREWarnings(object):

    """Extension that suppresses warnings."""

    def __init__(self, app=None):
        """Initialize the extension."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the application."""
        self.init_config(app)

        if not app.config['DEBUG_SHOW_DEPRECATION_WARNINGS']:
            warnings.filterwarnings('ignore', category=DeprecationWarning)

        app.extensions['inspire-warnings'] = self

    def init_config(self, app):
        """Initialize the configuration."""
        app.config.setdefault('DEBUG_SHOW_DEPRECATION_WARNINGS', False)
