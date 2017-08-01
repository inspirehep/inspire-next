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

from __future__ import absolute_import, division, print_function

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.hal.core.tei import _is_art, _is_comm


def test_is_art():
    schema = load_schema('hep')
    document_type_schema = schema['properties']['document_type']
    publication_info_schema = schema['properties']['publication_info']

    record = {
        'document_type': [
            'article',
        ],
        'publication_info': [
            {
                'journal_issue': '2',
                'journal_title': 'Phys.Part.Nucl.Lett.',
                'journal_volume': '14',
                'page_start': '336',
            },
        ],
    }
    assert validate(record['document_type'], document_type_schema) is None
    assert validate(record['publication_info'], publication_info_schema) is None

    assert _is_art(record)


def test_is_comm():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    record = {
        'document_type': [
            'conference paper',
        ],
    }
    assert validate(record['document_type'], subschema) is None

    assert _is_comm(record)
