# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

from __future__ import absolute_import, division, print_function

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.refextract import match_reference

from factories.db.invenio_records import TestRecordMetadata


def test_match_reference_for_jcap_and_jhep_config():
    """Test reference matcher for the JCAP and JHEP configuration"""

    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'control_number': 1,
        'document_type': ['article'],
        'publication_info': [
            {
                'artid': '045',
                'journal_title': 'JHEP',
                'journal_volume': '06',
                'page_start': '045',
                'year': 2007
            }
        ],
        'titles': [
            {
                'title': 'The Strongly-Interacting Light Higgs'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-hep')

    reference = {
        'reference': {
            'publication_info': {
                'artid': '045',
                'journal_title': 'JHEP',
                'journal_volume': '06',
                'page_start': '045',
                'year': 2007
            }
        }
    }

    schema = load_schema('hep')
    subschema = schema['properties']['references']

    assert validate([reference], subschema) is None

    reference = match_reference(reference)

    assert reference['record']['$ref'] == 'http://localhost:5000/api/literature/1'
    assert validate([reference], subschema) is None


def test_match_reference_for_data_config():
    """Test reference matcher for the JCAP and JHEP configuration"""

    cited_record_json = {
        '$schema': 'http://localhost:5000/schemas/records/data.json',
        '_collections': ['Data'],
        'control_number': 1,
        'dois': [
            {
                'value': '10.5281/zenodo.11020'
            }
        ],
    }

    TestRecordMetadata.create_from_kwargs(
        json=cited_record_json, index_name='records-data', pid_type='dat')

    reference = {
        'reference': {
            'dois': [
                '10.5281/zenodo.11020'
            ],
            'publication_info': {
                'year': 2007
            }
        }
    }

    reference = match_reference(reference)

    assert reference['record']['$ref'] == 'http://localhost:5000/api/data/1'
