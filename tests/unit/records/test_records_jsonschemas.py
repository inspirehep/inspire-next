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

from __future__ import absolute_import, division, print_function

import json
import os
import pkg_resources

from jsonschema import Draft4Validator


def fetch_schema(path):
    return json.loads(pkg_resources.resource_string('inspirehep', path))


def test_schemas_are_valid():
    root_dir = os.path.join(
        'inspirehep', 'modules', 'records', 'jsonschemas', 'records')
    for schemas_dir, _, schemas in os.walk(root_dir):
        schemas_path = os.path.sep.join(schemas_dir.split(os.path.sep)[1:])
        for schema in schemas:
            schema_path = os.path.join(schemas_path, schema)
            Draft4Validator.check_schema(fetch_schema(schema_path))
