# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.api import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


@pytest.mark.xfail(reason='Schema 13')
def test_HEP_added_to_980__a():
    '''
    HEP is not written explicitly in the record anymore,
    so it needs to be added in hep2marc.
    '''
    schema = load_schema('hep')

    snippet = ''
    result = hep.do(create_record(snippet))

    expected = [
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


@pytest.mark.xfail(reason='Schema 13')
def test_citeable_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">citeable</subfield>
        </datafield>
    '''

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['citeable'], subschema) is None
    assert expected == result['citeable']

    expected = [
        {'a': 'citeable'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


@pytest.mark.xfail(reason='Schema 13')
def test_core_from_980__a_core():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">CORE</subfield>
        </datafield>
    '''

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'CORE'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


@pytest.mark.xfail(reason='Schema 13')
def test_core_from_980__a_noncore():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">noncore</subfield>
        </datafield>
    '''

    expected = False
    result = hep.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']

    expected = [
        {'a': 'noncore'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


@pytest.mark.xfail(reason='Schema 13')
def test_special_collections_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['special_collections']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">HALhidden</subfield>
        </datafield>
    '''

    expected = ['HALHIDDEN']
    result = hep.do(create_record(snippet))

    assert validate(result['special_collections'], subschema) is None
    assert expected == result['special_collections']

    expected = [
        {'a': 'HALHIDDEN'}
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['980']


@pytest.mark.xfail(reason='Schema 13')
def test_refereed_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Published</subfield>
        </datafield>
    '''

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['refereed'], subschema) is None
    assert expected == result['refereed']

    expected = [
        { 'a': 'Published'},
        { 'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


@pytest.mark.xfail(reason='Schema 13')
def test_document_type_article_is_default():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = ''

    expected = ['article']
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    not_expected = {'a': 'article'}
    result = hep2marc.do(result)

    assert not_expected not in result['980']


@pytest.mark.xfail(reason='Schema 13')
def test_document_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Book</subfield>
        </datafield>
    '''

    expected = ['book']
    result = hep.do(create_record(snippet))

    assert validate(result['document_type'], subschema) is None
    assert expected == result['document_type']

    expected = [
        {'a': 'book'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


@pytest.mark.xfail(reason='Schema 13')
def test_publication_type_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['publication_type']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">Review</subfield>
        </datafield>
    '''

    expected = ['review']
    result = hep.do(create_record(snippet))

    assert validate(result['publication_type'], subschema) is None
    assert expected == result['publication_type']

    expected = [
        {'a': 'review'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])


@pytest.mark.xfail(reason='Schema 13')
def test_withdrawn_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['core']

    snippet = '''
        <datafield tag="980" ind1=" " ind2=" ">
          <subfield code="a">withdrawn</subfield>
        </datafield>
    '''

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['withdrawn'], subschema) is None
    assert expected == result['withdrawn']

    expected = [
        {'a': 'withdrawn'},
        {'a': 'HEP'}
    ]
    result = hep2marc.do(result)

    assert sorted(expected) == sorted(result['980'])
