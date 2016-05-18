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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

import glob

import inspirehep.dojson.utils as inspire_dojson_utils

import json
import os
import pkg_resources

from jsonschema import Draft4Validator


def fetch_schema(filename):
    return json.loads(
        pkg_resources.resource_string(
            'inspirehep',
            os.path.join(
                'modules',
                'records',
                'jsonschemas',
                'records',
                filename
            )
        )
    )

def test_schemas():

    schemas = [os.path.split(schema)[1] for schema in glob.glob(os.path.join(
        'inspirehep', 'modules', 'records', 'jsonschemas', 'records', '*.json'))]

    for schema in schemas:
        Draft4Validator.check_schema(fetch_schema(schema))



# def test_acquisition_source_schema_is_valid():
#     acquisition_source_schema = fetch_schema('acquisition_source.json')
#
#     Draft4Validator.check_schema(acquisition_source_schema)
#
#
# def test_authors_schema_is_valid():
#     authors_schema = fetch_schema('authors.json')
#
#     Draft4Validator.check_schema(authors_schema)
#
#
# def test_conferences_schema_is_valid():
#     conferences_schema = fetch_schema('conferences.json')
#
#     Draft4Validator.check_schema(conferences_schema)
#
#
# def test_experiments_schema_is_valid():
#     experiments_schema = fetch_schema('experiments.json')
#
#     Draft4Validator.check_schema(experiments_schema)
#
#
# def test_hep_schema_is_valid():
#     hep_schema = fetch_schema('hep.json')
#
#     Draft4Validator.check_schema(hep_schema)
#
#
# def test_institutions_schema_is_valid():
#     institutions_schema = fetch_schema('conferences.json')
#
#     Draft4Validator.check_schema(institutions_schema)
#
#
# def test_jobs_schema_is_valid():
#     jobs_schema = fetch_schema('jobs.json')
#
#     Draft4Validator.check_schema(jobs_schema)
#
#
# def test_journals_schema_is_valid():
#     journals_schema = fetch_schema('journals.json')
#
#     Draft4Validator.check_schema(journals_schema)
#
#
# def test_json_reference_schema_is_valid():
#     json_reference_schema = fetch_schema('json_reference.json')
#
#     Draft4Validator.check_schema(json_reference_schema)
