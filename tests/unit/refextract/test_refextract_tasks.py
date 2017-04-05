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

import os
import pkg_resources

from inspire_schemas.utils import load_schema
from inspirehep.dojson.utils import validate
from inspirehep.modules.refextract.tasks import (
    extract_journal_info,
    extract_references,
)


class StubObj(object):
    def __init__(self, data):
        self.data = data


class DummyEng(object):
    pass


def test_extract_journal_info():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)'},
        ],
    }
    assert validate(data['publication_info'], subschema) is None

    obj = StubObj(data)
    eng = DummyEng()

    assert extract_journal_info(obj, eng) is None
    assert validate(obj.data['publication_info'], subschema) is None
    assert obj.data['publication_info'] == [
        {
            'artid': '082102',
            'journal_title': 'J. Math. Phys.',
            'journal_volume': '55',
            'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)',
            'year': 2014,
        }
    ]


def test_extract_journal_info_handles_year_an_empty_string():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'pubinfo_freetext': (
                'The Astrophysical Journal, 838:134 (16pp), 2017 April 1')},
        ],
    }
    assert validate(data['publication_info'], subschema) is None

    obj = StubObj(data)
    eng = DummyEng()

    assert extract_journal_info(obj, eng) is None
    assert validate(obj.data['publication_info'], subschema) is None
    assert obj.data['publication_info'] == [
        {
            'artid': '134',
            'journal_title': 'Astrophys. J.',
            'journal_volume': '838',
            'page_start': '134',
            'pubinfo_freetext': (
                'The Astrophysical Journal, 838:134 (16pp), 2017 April 1'),
        },
    ]


def test_extract_references_handles_unicode():
    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1704.00452.pdf'))

    extract_references(filename)
