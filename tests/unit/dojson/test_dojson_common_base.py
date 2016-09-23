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

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.hepnames import hepnames, hepnames2marc


def test_acquisition_source_from__541_a_c():
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

    assert expected == result['acquisition_source']


def test_acquisition_source_from__541_double_a_b_c_e():
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
    result = hep.do(create_record(snippet))

    assert expected == result['acquisition_source']


def test_541__a_b_c_e_from_acquisition_source():
    record = {
        'acquisition_source': {
            'source': 'orcid:0000-0002-1048-661X',
            'email': 'oliver.schlotterer@web.de',
            'method': 'submission',
            'submission_number': '504296',
        },
    }

    expected = {
        'a': 'orcid:0000-0002-1048-661X',
        'b': 'oliver.schlotterer@web.de',
        'c': 'submission',
        'e': '504296',
    }
    result = hep2marc.do(record)

    assert expected == result['541']


def test_field_from_marcxml_650_with_single_a_and_9():
    """Simple case.

    One arXiv fieldcode that will be mapped to an INSPIRE category. Source
    will also be mapped to a standard term.
    """
    snippet = (
        '<record>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">HEP-PH</subfield>'
        '    <subfield code="9">automatically added based on DCC, PPF, DK </subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'source': 'INSPIRE',
            '_scheme': 'INSPIRE',
            'scheme': 'INSPIRE',
            '_term': 'HEP-PH',
            'term': 'Phenomenology-HEP',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['field_categories']


def test_field_from_marcxml_650_with_two_a():
    """Two 'a' subfields in one datafield.

    The first is an arXiv fieldcode an the second an INSPIRE category.
    """
    snippet = (
        '<record>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">hep-ex</subfield>'
        '    <subfield code="a">Gravitation and Cosmology</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            '_scheme': 'INSPIRE',
            'scheme': 'INSPIRE',
            '_term': 'hep-ex',
            'term': 'Experiment-HEP',
        },
        {
            '_scheme': 'INSPIRE',
            'scheme': 'INSPIRE',
            '_term': 'Gravitation and Cosmology',
            'term': 'Gravitation and Cosmology',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['field_categories']


def test_field_from_marcxml_650_with_two_2():
    """Two '2' subfields in one datafield.

    The first will be taken (this time it's correct).
    """
    snippet = (
        '<record>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="2">arXiv</subfield>'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">hep-ex</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            '_scheme': 'arXiv',
            'scheme': 'INSPIRE',
            '_term': 'hep-ex',
            'term': 'Experiment-HEP',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['field_categories']


def test_field_from_multiple_marcxml_650():
    """Two datafields.

    Both are arXiv field codes, but the other is incorrectly labeled as INSPIRE.
    """
    snippet = (
        '<record>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="2">arXiv</subfield>'
        '    <subfield code="a">HEP-PH</subfield>'
        '  </datafield>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="2">INSPIRE</subfield>'
        '    <subfield code="a">astro-ph.IM</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            '_scheme': 'arXiv',
            'scheme': 'INSPIRE',
            '_term': 'HEP-PH',
            'term': 'Phenomenology-HEP',
        },
        {
            '_scheme': 'INSPIRE',
            'scheme': 'INSPIRE',
            '_term': 'astro-ph.IM',
            'term': 'Instrumentation',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['field_categories']


def test_field_from_marcxml_650_with_no_a():
    """No term at all."""
    snippet = (
        '<record>'
        '  <datafield tag="650" ind1="1" ind2="7">'
        '    <subfield code="2">arXiv</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = hepnames.do(create_record(snippet))

    assert 'field_categories' not in result


def test_field_categories_from_650__a_2():
    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">Inspire</subfield>'
        '  <subfield code="a">Experiment-HEP</subfield>'
        '</datafield>'
    )  # record/1426196

    expected = [
        {
            '_scheme': 'Inspire',
            'scheme': 'INSPIRE',
            '_term': 'Experiment-HEP',
            'term': 'Experiment-HEP',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['field_categories']


def test_field_categories_from_65017_a_2_9_with_conference():
    snippet = (
        '<datafield tag="650" ind1="1" ind2="7">'
        '  <subfield code="2">INSPIRE</subfield>'
        '  <subfield code="9">conference</subfield>'
        '  <subfield code="a">Accelerators</subfield>'
        '</datafield>'
    )  # record/1479228

    expected = [
        {
            '_scheme': 'INSPIRE',
            'scheme': 'INSPIRE',
            'source': 'conference',
            '_term': 'Accelerators',
            'term': 'Accelerators',
        },
    ]
    result = hepnames.do(create_record(snippet))

    assert expected == result['field_categories']


def test_urls_from_marcxml_856_with_single_u_single_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="y">Conference web page</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/labastro/'
        }
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_single_u_two_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="y">Conference web page</subfield>'
        '    <subfield code="y">Not really the web page</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/labastro/'
        }
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_single_u_no_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_two_u_single_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="u">http://www.physics.unlv.edu/</subfield>'
        '    <subfield code="y">Conference web page</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_two_u_duplicates_single_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="y">Conference web page</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_two_u_two_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="u">http://www.physics.unlv.edu/</subfield>'
        '    <subfield code="y">Conference web page</subfield>'
        '    <subfield code="y">Not a description</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_two_u_no_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="u">http://www.physics.unlv.edu/</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
        {
            'value': 'http://www.physics.unlv.edu/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_urls_from_marcxml_multiple_8564():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2="">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '    <subfield code="y">Conference web page</subfield>'
        '  </datafield>'
        '  <datafield tag="856" ind1="4" ind2="">'
        '    <subfield code="u">http://www.cern.ch/</subfield>'
        '    <subfield code="y">CERN web page</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'description': 'Conference web page',
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
        {
            'description': 'CERN web page',
            'value': 'http://www.cern.ch/',
        },
    ]
    result = hep.do(create_record(snippet))

    assert expected == result['urls']


def test_collections_from_980__double_a_double_b():
    snippet = (
        '<record>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">Test_a1</subfield>'
        '    <subfield code="a">Test_a2</subfield>'
        '    <subfield code="b">Something</subfield>'
        '    <subfield code="b">Something else</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected_json = {
        'collections': [
            {
                'primary': 'Test_a1',
                'secondary': [
                    'Something',
                    'Something else',
                ],
            },
        ],
    }

    expected_marc = [
        {
            'a': 'Test_a1',
            'b': [
                'Something',
                'Something else',
            ],
        },
    ]

    json_result = hepnames.do(create_record(snippet))
    marc_result = hepnames2marc.do(json_result)

    assert expected_json['collections'] == json_result['collections']

    expected_marc.sort()
    marc_result['980'].sort()

    assert expected_marc == marc_result['980']
