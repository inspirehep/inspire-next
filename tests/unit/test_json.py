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

import json
import os.path

JSON_PATHS = [os.path.join('inspirehep', 'modules', 'records', 'jsonschemas'),
              os.path.join('inspirehep', 'modules', 'workflows', 'mappings'),
              os.path.join('inspirehep', 'modules', 'records', 'mappings')]


def pretty_json(json_content):
    out = json.dumps(json.loads(json_content), indent=4, sort_keys=True)
    # Let's strip trailing spaces and add newline at the end.
    return out.replace(', \n', ',\n') + '\n'


def test_pretty_json():
    for root_dir in JSON_PATHS:
        for json_dir, _, json_files in os.walk(root_dir):
            for json_file in json_files:
                if not json_file.endswith(".json"):
                    continue
                json_path = os.path.join(json_dir, json_file)
                json_content = open(json_path).read()
                assert json_content == pretty_json(json_content), "{file} is not pretty. Please run ./scripts/prettyjson before committing"
