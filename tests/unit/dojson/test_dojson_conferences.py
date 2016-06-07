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

from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.utils import strip_empty_values


def test_address_from_marcxml__111_c():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Austin, Tex.</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.'
        }
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_multiple_marcxml__111_c():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Austin, Tex.</subfield>'
        '  </datafield>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Den Haag, Nederlands</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.'
        },
        {
            'country_code': 'NL',
            'original_address': 'Den Haag, Nederlands'
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['address']


def test_address_from_marcxml__111_multiple_c():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="c">Austin, Tex.</subfield>'
        '    <subfield code="c">Den Haag, Nederlands</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'country_code': 'US',
            'state': 'US-TX',
            'original_address': 'Austin, Tex.'
        },
        {
            'country_code': 'NL',
            'original_address': 'Den Haag, Nederlands'
        }
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['address']


def test_contact_details_from_marcxml_270_single_p_single_m():
    snippet = (
        '<record> '
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '    <subfield code="p">Manfred Lindner</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'Manfred Lindner',
            'email': 'lindner@mpi-hd.mpg.de',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_double_p_single_m():
    """Two people having same e-mail address. We do not support it."""
    snippet = (
        '<record> '
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '    <subfield code="p">Manfred Lindner</subfield>'
        '    <subfield code="p">Boogeyman</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'email': 'lindner@mpi-hd.mpg.de',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_single_p_double_m():
    """One person having two e-mail addresses. We do not support it."""
    snippet = (
        '<record> '
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '    <subfield code="m">lindner@ecmrecords.com</subfield>'
        '    <subfield code="p">Manfred Lindner</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'Manfred Lindner'
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['contact_details']


def test_contact_details_from_multiple_marcxml_270():
    snippet = (
        '<record> '
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '    <subfield code="p">Manfred Lindner</subfield>'
        '  </datafield>'
        '  <datafield tag="270" ind1=" " ind2=" ">'
        '    <subfield code="p">Wynton Marsalis</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'name': 'Manfred Lindner',
            'email': 'lindner@mpi-hd.mpg.de',
        },
        {
            'name': 'Wynton Marsalis',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['contact_details']


def test_titles_from_marcxml_111():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="a">NASA Laboratory Astrophysics Workshop</subfield>'
        '    <subfield code="d">14-16 Feb 2006</subfield>'
        '    <subfield code="x">2006-02-14</subfield>'
        '    <subfield code="c">Las Vegas, Nevada</subfield>'
        '    <subfield code="g">C06-02-14</subfield>'
        '    <subfield code="y">2006-02-16</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'NASA Laboratory Astrophysics Workshop',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['titles']


def test_titles_from_marcxml_111_with_two_a():
    snippet = (
        '<record>'
        '  <datafield tag="111" ind1=" " ind2=" ">'
        '    <subfield code="a">Conférence IAP 2013</subfield>'
        '    <subfield code="a">75 Anniversary Conference</subfield>'
        '    <subfield code="b">The origin of the Hubble sequence</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': u'Conférence IAP 2013',
            'subtitle': 'The origin of the Hubble sequence',
        },
        {
            'title': '75 Anniversary Conference',
            'subtitle': 'The origin of the Hubble sequence',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['titles']


def test_alternative_titles_from_marcxml_711():
    snippet = (
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE16</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'GCACSE16',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['alternative_titles']


def test_alternative_titles_from_multiple_marcxml_711():
    snippet = (
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE16</subfield>'
        '  </datafield>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">GCACSE 2016</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'GCACSE16',
        },
        {
            'title': 'GCACSE 2016',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['alternative_titles']


def test_alternative_titles_marcxml_711_with_b():
    snippet = (
        '<record>'
        '  <datafield tag="711" ind1=" " ind2=" ">'
        '    <subfield code="a">XX Riunione Nazionale di Elettromagnetismo</subfield>'
        '    <subfield code="b">Padova</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'XX Riunione Nazionale di Elettromagnetismo',
            'searchable_title': 'Padova',
        },
    ]
    result = strip_empty_values(conferences.do(create_record(snippet)))

    assert expected == result['alternative_titles']
