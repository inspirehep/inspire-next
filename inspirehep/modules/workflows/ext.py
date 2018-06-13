# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Workflows extension."""

from __future__ import absolute_import, division, print_function

import os

import pkg_resources

from . import config
from .views import blueprint
from .workflows.views import blueprint as wf_blueprint


class InspireWorkflows(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.init_config(app)
        app.register_blueprint(blueprint)
        app.register_blueprint(wf_blueprint)
        app.extensions['inspire-workflows'] = self

    def init_config(self, app):
        for k in dir(config):
            if k.startswith('WORKFLOWS_'):
                app.config.setdefault(k, getattr(config, k))

        app.config.setdefault("WORKFLOWS_PENDING_RECORDS_CACHE_TIMEOUT",
                              2629743)
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
