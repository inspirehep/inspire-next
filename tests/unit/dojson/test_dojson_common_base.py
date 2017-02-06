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


def test_acquisition_source_from_541__a_c():
    schema = load_schema('elements/acquisition_source')

    snippet = (
        '<datafield tag="541" ind1=" " ind2=" ">'
        '  <subfield code="a">IOP</subfield>'
        '  <subfield code="c">batchupload</subfield>'
        '</datafield>'
    )  # record/1487640/export/xme

    expected = {
        'source': 'IOP',
        'method': 'batchupload',
    }
    result = hep.do(create_record(snippet))

    assert validate(result['acquisition_source'], schema) is None
    assert expected == result['acquisition_source']

    expected = {
        'a': 'IOP',
        'c': 'batchupload',
    }
    result = hep2marc.do(result)

    assert expected == result['541']


def test_acquisition_source_from_541__double_a_b_c_e():
    schema = load_schema('elements/acquisition_source')

    snippet = (
        '<datafield tag="541" ind1=" " ind2=" ">'
        '  <subfield code="a">inspire:uid:52524</subfield>'
        '  <subfield code="a">orcid:0000-0002-1048-661X</subfield>'
        '  <subfield code="b">oliver.schlotterer@web.de</subfield>'
        '  <subfield code="c">submission</subfield>'
        '  <subfield code="e">504296</subfield>'
        '</datafield>'
    )  # record/1416571/export/xme

    expected = {
        'source': 'orcid:0000-0002-1048-661X',
        'email': 'oliver.schlotterer@web.de',
        'method': 'submission',
        'submission_number': '504296',
    }
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['acquisition_source'], schema) is None
    assert expected == result['acquisition_source']

    expected = {
        'a': 'orcid:0000-0002-1048-661X',
        'b': 'oliver.schlotterer@web.de',
        'c': 'submission',
        'e': '504296',
    }
    result = hep2marc.do(result)

    assert expected == result['541']


def test_self_from_001():
    schema = load_schema('hep')
    subschema = schema['properties']['self']

    snippet = (
        '<controlfield tag="001">1508668</controlfield>'
    )  # record/1508668

    expected = {'$ref': 'http://localhost:5000/api/literature/1508668'}
    result = hep.do(create_record(snippet))

    assert validate(result['self'], subschema) is None
    assert expected == result['self']


def test_control_number_from_001():
    schema = load_schema('hep')
    subschema = schema['properties']['control_number']

    snippet = (
        '<controlfield tag="001">1508668</controlfield>'
    )  # record/1508668

    expected = 1508668
    result = hep.do(create_record(snippet))

    assert validate(result['control_number'], subschema) is None
    assert expected == result['control_number']

    expected = 1508668
    result = hep2marc.do(result)

    assert expected == result['001']


@pytest.mark.xfail(reason='missing roundtrip')
def test_external_system_numbers_from_970__a():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_numbers']

    snippet = (
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">SPIRES-10325093</subfield>'
        '</datafield>'
    )  # record/1297176

    expected = [
        {
            'institute': 'SPIRES',
            'obsolete': True,
            'value': 'SPIRES-10325093',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_numbers'], subschema) is None
    assert expected == result['external_system_numbers']

    expected = [
        {'a': 'SPIRES-10325093'},
    ]
    result = hep2marc.do(result)

    assert expected == result['970']


@pytest.mark.xfail(reason='missing roundtrip')
def test_external_system_numbers_from_970__double_a():
    schema = load_schema('hep')
    subschema = schema['properties']['external_system_numbers']

    snippet = (
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="a">SPIRES-9663061</subfield>'
        '  <subfield code="a">SPIRES-9949933</subfield>'
        '</datafield>'
    )  # record/1217763

    expected = [
        {
            'institute': 'SPIRES',
            'obsolete': True,
            'value': 'SPIRES-9663061',
        },
        {
            'institute': 'SPIRES',
            'obsolete': True,
            'value': 'SPIRES-9949933',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['external_system_numbers'], subschema) is None
    assert expected == result['external_system_numbers']

    expected = [
        {'a': 'SPIRES-9663061'},
        {'a': 'SPIRES-9949933'},
    ]
    result = hep2marc.do(result)

    assert expected == result['970']


@pytest.mark.xfail(reason='wrong roundtrip')
def test_new_record_from_970__d():
    schema = load_schema('hep')
    subschema = schema['properties']['new_record']

    snippet = (
        '<datafield tag="970" ind1=" " ind2=" ">'
        '  <subfield code="d">361769</subfield>'
        '</datafield>'
    )  # record/37545

    expected = {'$ref': 'http://localhost:5000/api/record/361769'}
    result = hep.do(create_record(snippet))

    assert validate(result['new_record'], subschema) is None
    assert expected == result['new_record']

    expected = {'d': '361769'}
    result = hep2marc.do(result)

    assert expected == result['970']


def test_collections_from_980__a():
    schema = load_schema('hep')
    subschema = schema['properties']['collections']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="a">HEP</subfield>'
        '</datafield>'
    )  # record/1508886

    expected = [
        {'primary': 'HEP'},
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['collections'], subschema) is None
    assert expected == result['collections']

    expected = [
        {'a': 'HEP'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_deleted_from_980__c():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted']

    snippet = (
        '<datafield tag="980" ind1=" " ind2=" ">'
        '  <subfield code="c">DELETED</subfield>'
        '</datafield>'
    )  # record/1508668/export/xme

    expected = True
    result = hep.do(create_record(snippet))

    assert validate(result['deleted'], subschema) is None
    assert expected == result['deleted']

    expected = [
        {'c': 'DELETED'},
    ]
    result = hep2marc.do(result)

    assert expected == result['980']


def test_deleted_records_from_981__a():
    schema = load_schema('hep')
    subschema = schema['properties']['deleted_records']

    snippet = (
        '<datafield tag="981" ind1=" " ind2=" ">'
        '  <subfield code="a">1508668</subfield>'
        '</datafield>'
    )  # record/1508886

    expected = [{'$ref': 'http://localhost:5000/api/record/1508668'}]
    result = hep.do(create_record(snippet))

    assert validate(result['deleted_records'], subschema) is None
    assert expected == result['deleted_records']

    expected = [
        {'a': 1508668},
    ]
    result = hep2marc.do(result)

    assert expected == result['981']


def test_inspire_categories_from_65017a_2():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">Inspire</subfield>'
        '  <subfield code="a">Experiment-HEP</subfield>'
        '</datafield>'
    )  # record/1426196

    expected = [
        {
            'source': 'undefined',
            'term': 'Experiment-HEP',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '9': 'undefined',
            'a': 'Experiment-HEP',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_9_discards_conference():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="9">conference</subfield>'
        '  <subfield code="a">Accelerators</subfield>'
        '</datafield>'
    )  # record/1479228

    expected = [
        {
            'source': 'undefined',
            'term': 'Accelerators',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '9': 'undefined',
            'a': 'Accelerators',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_9_converts_automatically_added():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="a">Instrumentation</subfield>'
        '  <subfield code="9">automatically added based on DCC, PPF, DK</subfield>'
        '</datafield>'
    )  # record/669400

    expected = [
        {
            'source': 'curator',
            'term': 'Instrumentation',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '9': 'curator',
            'a': 'Instrumentation',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_inspire_categories_from_65017a_2_9_converts_submitter():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="a">Math and Math Physics</subfield>'
        '  <subfield code="9">submitter</subfield>'
        '  <subfield code="2">INSPIRE</subfield>'
        '</datafield>'
    )  # record/1511089

    expected = [
        {
            'source': 'user',
            'term': 'Math and Math Physics',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['inspire_categories'], subschema) is None
    assert expected == result['inspire_categories']

    expected = [
        {
            '9': 'user',
            'a': 'Math and Math Physics'
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['65017']


def test_fft_from_FFT_a_d_f_n_o_t():
    snippet = (
        '<datafield tag="FFT">'
        '  <subfield code="a">url</subfield>'
        '  <subfield code="t">docfile_type</subfield>'
        '  <subfield code="o">flag</subfield>'
        '  <subfield code="d">description</subfield>'
        '  <subfield code="n">filename</subfield>'
        '  <subfield code="f">filetype</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'url': 'url',
            'docfile_type': 'docfile_type',
            'flag': 'flag',
            'description': 'description',
            'filename': 'filename',
            'filetype': 'filetype',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['fft']

    expected = [
        {
            'a': 'url',
            't': 'docfile_type',
            'o': 'flag',
            'd': 'description',
            'n': 'filename',
            'f': 'filetype',
        },
    ]
    result = hep2marc.do(hep.do(create_record(snippet)))

    assert expected == result['FFT']


def test_urls_from_8564_u_y():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="u">http://www-lib.kek.jp/ar/ar.html</subfield>'
        '  <subfield code="y">KEK</subfield>'
        '</datafield>'
    )  # record/1405358

    expected = [
        {
            'description': 'KEK',
            'value': 'http://www-lib.kek.jp/ar/ar.html',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://www-lib.kek.jp/ar/ar.html',
            'y': 'KEK',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_s_u_ignores_s():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="s">443981</subfield>'
        '  <subfield code="u">http://inspirehep.net/record/1511347/files/HIG-16-034-pas.pdf</subfield>'
        '</datafield>'
    )  # record/1511347

    expected = [
        {'value': 'http://inspirehep.net/record/1511347/files/HIG-16-034-pas.pdf'},
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {'u': 'http://inspirehep.net/record/1511347/files/HIG-16-034-pas.pdf'},
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_u_w_y_ignores_w():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="w">12-316</subfield>'
        '  <subfield code="y">FERMILABPUB</subfield>'
        '  <subfield code="u">http://lss.fnal.gov/cgi-bin/find_paper.pl?pub-12-316</subfield>'
        '</datafield>'
    )  # record/1120360

    expected = [
        {
            'description': 'FERMILABPUB',
            'value': 'http://lss.fnal.gov/cgi-bin/find_paper.pl?pub-12-316',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://lss.fnal.gov/cgi-bin/find_paper.pl?pub-12-316',
            'y': 'FERMILABPUB',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']


def test_urls_from_8564_u_double_y_selects_the_first_y():
    schema = load_schema('hep')
    subschema = schema['properties']['urls']

    snippet = (
        '<datafield tag="856" ind1="4" ind2=" ">'
        '  <subfield code="u">http://link.springer.com/journal/10909/176/5/page/1</subfield>'
        '  <subfield code="y">Part II</subfield>'
        '  <subfield code="y">Springer</subfield>'
        '</datafield>'
    )  # record/1312672

    expected = [
        {
            'description': 'Part II',
            'value': 'http://link.springer.com/journal/10909/176/5/page/1',
        },
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['urls'], subschema) is None
    assert expected == result['urls']

    expected = [
        {
            'u': 'http://link.springer.com/journal/10909/176/5/page/1',
            'y': 'Part II',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['8564']
