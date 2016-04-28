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
from inspirehep.dojson.institutions import institutions
from inspirehep.dojson.utils import strip_empty_values


def test_address_from_marcxml_371__a_b_c_d_e_g():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Heidelberg",
        "country": "Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", ),
        "postal_code": "69120"
        }
                                 ]


def test_address_from_marcxml_371__double_a_b_c_d_e_g():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="a">Heidelberg</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Heidelberg",
        "country": "Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", "Heidelberg"),
        "postal_code": "69120"
        }
                                 ]


def test_address_from_marcxml_371__a_double_b_c_d_e_g():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="b">Altstadt</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Altstadt, Heidelberg",
        "country": "Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", ),
        "postal_code": "69120"
        }
                                 ]


def test_address_from_marcxml_371__a_b_c_double_d_e_g():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="d">Deutschland</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Heidelberg",
        "country": "Deutschland, Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", ),
        "postal_code": "69120"
        }
                                 ]


def test_address_from_marcxml_371__a_b_c_d_double_e_g():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="e">DE-119</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Heidelberg",
        "country": "Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", ),
        "postal_code": "69120, DE-119"
        }
                                 ]


def test_address_from_marcxml_371__a_b_c_d_e_double_g():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="g">DE</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Heidelberg",
        "country": "Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", ),
        "postal_code": "69120"
        }
                                 ]


def test_address_from_multiple_marcxml_371__a_b_c_d_e_g():
    snippet = (
        '<record> '
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="a">Philosophenweg 16</subfield>'
        '<subfield code="b">Heidelberg</subfield>'
        '<subfield code="c">Baden-Wuerttemberg</subfield>'
        '<subfield code="d">Germany</subfield>'
        '<subfield code="e">69120</subfield>'
        '<subfield code="g">DE</subfield>'
        '</datafield>'
        '<datafield tag="371" ind1=" " ind2=" ">'
        '<subfield code="e">88003</subfield>'
        '<subfield code="a">Physical Science Lab</subfield>'
        '<subfield code="a">Las Cruces, NM 88003</subfield>'
        '<subfield code="b">Las Cruces</subfield>'
        '<subfield code="c">New Mexico</subfield>'
        '<subfield code="d">USA</subfield>'
        '<subfield code="g">US</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(institutions.do(create_record(snippet)))
    assert record['address'] == [{
        "city": "Heidelberg",
        "country": "Germany",
        "country_code": "DE",
        "state": "Baden-Wuerttemberg",
        "original_address": ("Philosophenweg 16", ),
        "postal_code": "69120"
        },
        {
        "city": "Las Cruces",
        "country": "USA",
        "country_code": "US",
        "state": "US-NM",
        "original_address": ("Physical Science Lab", "Las Cruces, NM 88003", ),
        "postal_code": "88003"
        }
                                 ]
