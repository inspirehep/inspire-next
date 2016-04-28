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
