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

import json

from freezegun import freeze_time
from inspirehep.modules.records.serializers.schemas.latex import LatexSchema


@freeze_time("1994-12-19")
def test_full_schema():
    TODAY = "19 Dec 1994"
    schema = LatexSchema()
    record = {
        'texkeys': [
            'a123bx'
        ],
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        'authors': [
            {
                'full_name': 'Castle, Frank',
            },
            {
                'full_name': 'Smith, John',
            },
            {
                'full_name': 'Black, Joe Jr.',
            },
            {
                'full_name': 'Jimmy',
            },
        ],
        'collaborations': [{
            'value': 'LHCb',
        }],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'page_start': '500',
            'page_end': '593',
            'artid': '17920',
            'year': '2014'
        }],
        'report_numbers': [{
            'value': 'DESY-17-036'
        }]
    }
    expected = {
        'texkeys': 'a123bx',
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        'authors': [
            'F.~Castle',
            'J.~Smith',
            'J.~Black, Jr.',
            'Jimmy'
        ],
        'collaborations': [
            'LHCb'
        ],
        'dois': [
            {
                'value': '10.1088/1361-6633/aa5514',
            },
        ],
        'arxiv_eprints': [
            {
                'value': '1607.06746',
                'categories': ['hep-th']
            },
        ],
        'publication_info': {
            'journal_title': 'Phys.\\ Rev.\\ A',
            'journal_volume': '58',
            'page_start': '500',
            'page_end': '593',
            'page_range': '500-593',
            'artid': '17920',
            'year': '2014'
        },
        'report_numbers': [{
            'value': 'DESY-17-036'
        }],
        'citations': 0,
        'today': TODAY
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result


def test_authors_schema():
    schema = LatexSchema()
    record = {
        'control_number': '1',
        'authors': [
            {
                'full_name': 'Castle, Frank',
            },
            {
                'full_name': 'Smith, John',
            },
            {
                'full_name': 'Black, Joe Jr.',
            },
            {
                'full_name': 'Jimmy',
            },
        ],
    }
    expected = [
        'F.~Castle',
        'J.~Smith',
        'J.~Black, Jr.',
        'Jimmy'
    ]
    result = json.loads(schema.dumps(record).data)
    assert expected == result['authors']


def test_publication_info_schema():
    schema = LatexSchema()
    record = {
        'control_number': '1',
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'page_start': '500',
            'page_end': '593',
            'artid': '17920',
            'year': '2014'
        }],
    }
    expected = {
        'journal_title': 'Phys.\\ Rev.\\ A',
        'journal_volume': '58',
        'page_start': '500',
        'page_end': '593',
        'page_range': '500-593',
        'artid': '17920',
        'year': '2014'
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result['publication_info']


def test_publication_info_does_not_generate_page_range_with_page_end():
    schema = LatexSchema()
    record = {
        'control_number': '1',
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'page_end': '500',
            'artid': '17920',
            'year': '2014'
        }],
    }
    expected = {
        'journal_title': 'Phys.\\ Rev.\\ A',
        'journal_volume': '58',
        'page_end': '500',
        'artid': '17920',
        'year': '2014'
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result['publication_info']


def test_publication_info_generates_page_range_with_page_start():
    schema = LatexSchema()
    record = {
        'control_number': '1',
        'publication_info': [{
            'journal_title': 'Phys.Rev.A',
            'journal_volume': '58',
            'page_start': '500',
            'artid': '17920',
            'year': '2014'
        }],
    }
    expected = {
        'journal_title': 'Phys.\\ Rev.\\ A',
        'journal_volume': '58',
        'page_start': '500',
        'page_range': '500',
        'artid': '17920',
        'year': '2014'
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result['publication_info']


def test_publication_info_without_journal_title_schema():
    schema = LatexSchema()
    record = {
        'control_number': '1',
        'publication_info': [{
            'journal_volume': '58',
            'page_start': '500',
            'page_end': '593',
            'artid': '17920',
            'year': '2014'
        }],
    }
    expected = {
        'journal_volume': '58',
        'page_start': '500',
        'page_end': '593',
        'page_range': '500-593',
        'artid': '17920',
        'year': '2014'
    }
    result = json.loads(schema.dumps(record).data)
    assert expected == result['publication_info']


def test_schema_takes_control_number_when_texkeys_not_present():
    schema = LatexSchema()
    record = {
        'control_number': '123456',
    }
    expected = '123456'
    result = json.loads(schema.dumps(record).data)
    assert expected == result['texkeys']
