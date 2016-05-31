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

import os
import pkg_resources

from .views import blueprints


class INSPIREWorkflows(object):
    """INSPIRE workflows extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, assets=None, **kwargs):
        """Initialize application object."""
        self.init_config(app)
        for blueprint in blueprints:
            app.register_blueprint(blueprint)
        app.extensions['inspire-workflows'] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault("WORKFLOWS_MATCH_REMOTE_SERVER_URL",
                              app.config["SERVER_NAME"])
        app.config.setdefault("WORKFLOWS_PENDING_RECORDS_CACHE_TIMEOUT",
                              2629743)
        app.config.setdefault("HOLDING_PEN_MATCH_MAPPING", dict(
            doi="dois.value",
            eprint="arxiv_eprints.value",
            isbn="isbns.value",
            external_system_numbers="external_system_numbers.value",
        ))
        app.config["WORKFLOWS_STORAGEDIR"] = os.path.join(
            app.instance_path, "workflows", "storage"
        )
        app.config["WORKFLOWS_FILE_LOCATION"] = os.path.join(
            app.config['BASE_FILES_LOCATION'],
            "workflows", "files"
        )
        app.config['CLASSIFIER_WORKDIR'] = pkg_resources.resource_filename(
            'inspirehep', "taxonomies"
        )
