# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from dojson.contrib.marc21.utils import create_record
from inspirehep.dojson.conferences import conferences
from inspirehep.dojson.utils import strip_empty_values


def test_extra_place_info_from_marcxml_270_with_single_b():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="b">Grand Hotel dei Castelli</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['extra_place_info'] == ['Grand Hotel dei Castelli']


def test_extra_place_info_from_marcxml_270_with_double_b():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="b">Fermilab Illinois</subfield>'
        '<subfield code="b">Institute of Quantum Physics</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['extra_place_info'] == ['Fermilab Illinois',
                                          'Institute of Quantum Physics']


def test_extra_place_info_from_double_marcxml_270():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="b">Fermilab Illinois</subfield>'
        '</datafield>'
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="b">Institute of Quantum Physics</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['extra_place_info'] == ['Fermilab Illinois',
                                          'Institute of Quantum Physics']


def test_contact_details_from_marcxml_270_single_p_single_m():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '<subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['contact_details'] == [{
        'name': 'Manfred Lindner',
        'email': 'lindner@mpi-hd.mpg.de'
        }
                                         ]


def test_contact_details_from_marcxml_270_double_p_single_m():
    """Two people having same e-mail address. We do not support it."""
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '<subfield code="p">Manfred Lindner</subfield>'
        '<subfield code="p">Boogeyman</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['contact_details'] == [{
        'email': 'lindner@mpi-hd.mpg.de'
        }
                                         ]


def test_contact_details_from_marcxml_270_single_p_double_m():
    """One person having two e-mail addresses. We do not support it."""
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '<subfield code="m">lindner@ecmrecords.com</subfield>'
        '<subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['contact_details'] == [{
        'name': 'Manfred Lindner'
        }
                                         ]


def test_contact_details_from_multiple_marcxml_270():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '<subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="p">Wynton Marsalis</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['contact_details'] == [{
        'name': 'Manfred Lindner',
        'email': 'lindner@mpi-hd.mpg.de'
        },
                                         {
                                             'name': 'Wynton Marsalis'
                                         }
                                         ]


def test_address_from_marcxml__111_c():
    snippet = (
        '<record>'
        '<datafield tag="111" ind1=" " ind2=" ">'
        '<subfield code="c">Austin, Tex.</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['address'] == [{'country_code': 'US', 'state': 'US-TX',
                                  'original address': 'Austin, Tex.'}]


def test_address_from_multiple_marcxml__111_c():
    snippet = (
        '<record>'
        '<datafield tag="111" ind1=" " ind2=" ">'
        '<subfield code="c">Austin, Tex.</subfield>'
        '</datafield>'
        '<datafield tag="111" ind1=" " ind2=" ">'
        '<subfield code="c">Den Haag, Nederlands</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['address'] == [{'country_code': 'US', 'state': 'US-TX',
                                  'original address': 'Austin, Tex.'},
                                  {'country_code': 'NL',
                                  'original address': 'Den Haag, Nederlands'}
                                 ]


def test_address_from_marcxml__111_multiple_c():
    snippet = (
        '<record>'
        '<datafield tag="111" ind1=" " ind2=" ">'
        '<subfield code="c">Austin, Tex.</subfield>'
        '<subfield code="c">Den Haag, Nederlands</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    assert record['address'] == [{'country_code': 'US', 'state': 'US-TX',
                                  'original address': 'Austin, Tex.'},
                                  {'country_code': 'NL',
                                  'original address': 'Den Haag, Nederlands'}
                                 ]

def test_titles_from_marcxml_111():
    """Test title."""
    snippet = ( 
        '<record> '
        '<datafield tag="111" ind1=" " ind2=" "> '
        '<subfield code="a">NASA Laboratory Astrophysics Workshop</subfield> '
        '<subfield code="d">14-16 Feb 2006</subfield> '
        '<subfield code="x">2006-02-14</subfield> '
        '<subfield code="c">Las Vegas, Nevada</subfield> '
        '<subfield code="g">C06-02-14</subfield> '
        '<subfield code="y">2006-02-16</subfield> '
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    title = 'NASA Laboratory Astrophysics Workshop'
    assert record['titles'][0]['title'] == title


def test_titles_from_marcxml_111_with_two_a():
    """Test title."""
    snippet = ( 
        '<record> '
        '<datafield tag="111" ind1=" " ind2=" "> '
        '<subfield code="a">Conférence IAP 2013</subfield> '
        '<subfield code="a">75 Anniversary Conference</subfield> '
        '<subfield code="b">The origin of the Hubble sequence</subfield> '
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    title1 = u'Conférence IAP 2013'
    subtitle1 = 'The origin of the Hubble sequence'
    title2 = '75 Anniversary Conference'
    subtitle2 = 'The origin of the Hubble sequence'
    assert record['titles'][0]['title'] == title1
    assert record['titles'][0]['subtitle'] == subtitle1
    assert record['titles'][1]['title'] == title2
    assert record['titles'][1]['subtitle'] == subtitle2


def test_alternative_titles_from_marcxml_711():
    """Test alternative title."""
    snippet = ( 
        '<record> '
        '<datafield tag="711" ind1=" " ind2=" "> '
        '<subfield code="a">GCACSE16</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    title = 'GCACSE16'
    assert record['alternative_titles'][0]['title'] == title


def test_alternative_titles_from_multiple_marcxml_711():
    """Test multiple alternative titles."""
    snippet = ( 
        '<record> '
        '<datafield tag="711" ind1=" " ind2=" "> '
        '<subfield code="a">GCACSE16</subfield> '
        '</datafield> '
        '<datafield tag="711" ind1=" " ind2=" "> '
        '<subfield code="a">GCACSE 2016</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    title0 = 'GCACSE16'
    title1 = 'GCACSE 2016'
    assert record['alternative_titles'][0]['title'] == title0
    assert record['alternative_titles'][1]['title'] == title1


def test_alternative_titles_marcxml_711_with_b():
    """Test multiple alternative titles."""
    snippet = ( 
        '<record> '
        '<datafield tag="711" ind1=" " ind2=" "> '
        '<subfield code="a">XX Riunione Nazionale di Elettromagnetismo</subfield> '
        '<subfield code="b">Padova</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(conferences.do(create_record(snippet)))
    title = 'XX Riunione Nazionale di Elettromagnetismo'
    searchable_title = 'Padova'
    assert record['alternative_titles'][0]['title'] == title
    assert record['alternative_titles'][0]['searchable_title'] == searchable_title
