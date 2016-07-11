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

from inspirehep.dojson.hep import hep
from inspirehep.dojson.hepnames import hepnames

from inspirehep.dojson.utils import clean_record


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
    result = clean_record(hepnames.do(create_record(snippet)))

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
    result = clean_record(hepnames.do(create_record(snippet)))

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
    result = clean_record(hepnames.do(create_record(snippet)))

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
    result = clean_record(hepnames.do(create_record(snippet)))

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

    result = clean_record(hepnames.do(create_record(snippet)))

    assert 'field_categories' not in result


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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['urls']


def test_urls_from_marcxml_856_with_single_u_no_y():
    snippet = (
        '<record>'
        '  <datafield tag="856" ind1="4" ind2=" ">'
        '    <subfield code="u">http://www.physics.unlv.edu/labastro/</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected= [
        {
            'value': 'http://www.physics.unlv.edu/labastro/',
        },
    ]
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

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
    result = clean_record(hep.do(create_record(snippet)))

    assert expected == result['urls']
