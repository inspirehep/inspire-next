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

"""Unit tests for the TEI exporter."""

import mock
import pytest

from invenio_records.api import Record

from inspirehep.modules.hal import tei


@mock.patch('inspirehep.modules.hal.tei.get_es_records')
def test_parse_structures_no_authors(g_e_r):
    g_e_r.return_value = []

    no_authors = Record({})

    expected = []
    result = tei._parse_structures(no_authors)

    assert expected == result


@mock.patch('inspirehep.modules.hal.tei.get_es_records')
def test_parse_structures_one_author_no_affiliations(g_e_r):
    g_e_r.return_value = []

    one_author_no_affiliations = Record({
        'authors': [{}]
    })

    expected = []
    result = tei._parse_structures(one_author_no_affiliations)

    assert expected == result


@mock.patch('inspirehep.modules.hal.tei.get_es_records')
def test_parse_structures_one_author_invalid_affiliation_record(g_e_r):
    g_e_r.return_value = []

    one_author_invalid_affiliation_record = Record({
        'authors': [
            {'affiliations':
                [{'record':
                    {'$ref': "http://localhost:5000/api/institutions/902943"}
                  }
                 ]
             }
        ]
    })

    expected = []
    result = tei._parse_structures(one_author_invalid_affiliation_record)

    assert expected == result


@mock.patch('inspirehep.modules.hal.tei.get_es_records')
def test_parse_structures_one_author_one_affiliation_record(g_e_r):
    g_e_r.return_value = [{
        'institution':
        ['Joint Institute for Nuclear Research (JINR)'],
        'address':
        [
            {'original_address':
             ['Joliot-Curie 6',
              '141980, Dubna',
              'Moscow Region'],
             'country_code': 'RU'
             }
        ],
        'collections': [None,
                        {'primary': 'INSTITUTION'}],
        'self': {'$ref': "http://localhost:5000/api/institutions/902780"},
    }]

    one_author_one_affiliation_record = Record({
        'authors': [
            {'affiliations':
                [
                    {'record':
                     {'$ref': "http://localhost:5000/api/institutions/902780"}
                     }
                ]
             }
        ]
    })

    expected = [{'country': 'RU',
                 'address': ['Joliot-Curie 6',
                             '141980, Dubna',
                             'Moscow Region'],
                 'recid': 902780,
                 'name': 'Joint Institute for Nuclear Research (JINR)',
                 'type': 'institution',
                 }
                ]
    result = tei._parse_structures(one_author_one_affiliation_record)

    assert expected == result


def test_parse_pub_info_not_journal_or_conference():
    not_journal_or_conference = Record({
        'publication_info': [None]
    })

    result = tei._parse_pub_info(not_journal_or_conference)

    assert result is None


def test_parse_pub_info_journal():
    journal = Record({
        'publication_info': [
            {'journal_title': "JHEP",
             'journal_volume': "1603",
             'page_start': "165",
             'year': 2016}]
    })

    expected = {'type': "journal",
                'name': "JHEP",
                'year': 2016,
                'volume': "1603",
                'issue': "",
                'pp': "165"}

    result = tei._parse_pub_info(journal)

    assert expected == result


@mock.patch('inspirehep.modules.hal.tei.replace_refs')
def test_parse_pub_info_invalid_conference_record(r_r):
    r_r.return_value = None

    conference = {
        'publication_info': [
            {'conference_record':
                {'$ref': "http://localhost:5000/api/conferences/1320036"}
             }
        ]
    }

    expected = {
        'type': "conference",
        'name': "",
        'acronym': "",
        'opening_date': "",
        'closing_date': ""}

    result = tei._parse_pub_info(conference)

    assert expected == result


@mock.patch('inspirehep.modules.hal.tei.replace_refs')
def test_parse_pub_info_conference(r_r):
    r_r.return_value = {
        'titles': [{'title':
                    "18th International Seminar on High Energy Physics"}],
        'acronym': ["Quarks 2014"],
        'opening_date': "2014-06-02",
        'closing_date': "2014-06-08"}

    conference = {
        'publication_info': [
            {'conference_record':
                {'$ref': "http://localhost:5000/api/conferences/1320036"}
             }
        ]
    }

    expected = {
        'type': "conference",
        'name': "18th International Seminar on High Energy Physics",
        'acronym': "Quarks 2014",
        'opening_date': "2014-06-02",
        'closing_date': "2014-06-08"}

    result = tei._parse_pub_info(conference)

    assert expected == result


@mock.patch('inspirehep.modules.hal.tei.HumanName')
def test_parse_authors(HN):
    HN.return_value = {
        'title': "",
        'first': "A.N.",
        'middle': "",
        'last': "Skachkova",
        'suffix': "",
        'nickname': ""
    }

    authors = {
        'authors': [
            {'full_name': "Skachkova, A.N."}
        ]
    }

    expected = [{
        'full_name': "Skachkova, A.N.",
        'parsed_name':
            {'title': "",
             'first': "A.N.",
             'middle': "",
             'last': "Skachkova",
             'suffix': "",
             'nickname': ""}
    }]

    result = tei._parse_authors(authors)

    assert expected == result
