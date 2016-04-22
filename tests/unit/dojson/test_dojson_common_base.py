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
from inspirehep.dojson.hep import hep
from inspirehep.dojson.utils import strip_empty_values


def test_urls_from_marcxml_856_with_single_u_single_y():
    """Simple case."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="y">Conference web page</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'description': 'Conference web page',
        'value': 'http://www.physics.unlv.edu/labastro/'
    }]


def test_urls_from_marcxml_856_with_single_u_two_y():
    """Two descriptions on one url."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="y">Conference web page</subfield> '
        '<subfield code="y">Not really the web page</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'description': 'Conference web page',
        'value': 'http://www.physics.unlv.edu/labastro/'
    }]


def test_urls_from_marcxml_856_with_single_u_no_y():
    """No description."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'value': 'http://www.physics.unlv.edu/labastro/'
    }]


def test_urls_from_marcxml_856_with_two_u_single_y():
    """Two urls, one description."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="y">Conference web page</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'description': 'Conference web page',
        'value': 'http://www.physics.unlv.edu/labastro/'},
        {'description': 'Conference web page',
         'value': 'http://www.physics.unlv.edu/labastro/'
         }]


def test_urls_from_marcxml_856_with_two_u_two_y():
    """Two urls, two descriptions."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="y">Conference web page</subfield> '
        '<subfield code="y">Not a description</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'description': 'Conference web page',
        'value': 'http://www.physics.unlv.edu/labastro/'},
        {'description': 'Conference web page',
         'value': 'http://www.physics.unlv.edu/labastro/'
         }]


def test_urls_from_marcxml_856_with_two_u_no_y():
    """Two urls, no description."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'value': 'http://www.physics.unlv.edu/labastro/'},
        {'value': 'http://www.physics.unlv.edu/labastro/'
         }]


def test_urls_from_marcxml_multiple_8564():
    """Multiple 8564 fields with normal subfields."""
    snippet = (
        '<record> '
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.physics.unlv.edu/labastro/</subfield> '
        '<subfield code="y">Conference web page</subfield> '
        '</datafield>'
        '<datafield tag="856" ind1="4" ind2=" "> '
        '<subfield code="u">http://www.cern.ch/</subfield> '
        '<subfield code="y">CERN web page</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(hep.do(create_record(snippet)))
    assert record["urls"] == [{
        'description': 'Conference web page',
        'value': 'http://www.physics.unlv.edu/labastro/'},
        {'description': 'CERN web page', 'value': 'http://www.cern.ch/'
         }]
