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


def test_single_doi():
    snippet_single_doi = ('<record><datafield tag="024" ind1="7" ind2=" ">'
                               '<subfield code="2">DOI</subfield>'
                               '<subfield code="a">10.1088/0264-9381/31/24/245004</subfield>'
                               '</datafield></record>')

    x = create_record(snippet_single_doi)
    assert (strip_empty_values(hep.do(x))['dois'] ==
            [{'value': '10.1088/0264-9381/31/24/245004'}])


def test_duplicate_doi():
    snippet_duplicate_doi = ('<record><datafield tag="024" ind1="7" ind2=" ">'
                             '<subfield code="2">DOI</subfield>'
                             '<subfield code="9">bibmatch</subfield>'
                             '<subfield code="a">10.1088/1475-7516/2015/03/044</subfield>'
                             '</datafield>'
                             '<datafield tag="024" ind1="7" ind2=" ">'
                             '<subfield code="2">DOI</subfield>'
                             '<subfield code="a">10.1088/1475-7516/2015/03/044</subfield>'
                             '</datafield></record>')

    x = create_record(snippet_duplicate_doi)
    assert (strip_empty_values(hep.do(x))['dois'] ==
            [{'source': 'bibmatch', 'value': '10.1088/1475-7516/2015/03/044'},
             {'value': '10.1088/1475-7516/2015/03/044'}])


def test_multiple_dois():
    snippet_multiple_dois = ('<record><datafield tag="024" ind1="7" ind2=" ">'
                             '<subfield code="2">DOI</subfield>'
                             '<subfield code="a">10.1103/PhysRevD.89.072002</subfield>'
                             '</datafield>'
                             '<datafield tag="024" ind1="7" ind2=" ">'
                             '<subfield code="2">DOI</subfield>'
                             '<subfield code="9">bibmatch</subfield>'
                             '<subfield code="a">10.1103/PhysRevD.91.019903</subfield>'
                             '</datafield></record>')

    x = create_record(snippet_multiple_dois)
    assert (strip_empty_values(hep.do(x))['dois'] ==
            [{'value': '10.1103/PhysRevD.89.072002'},
             {'source': 'bibmatch', 'value': '10.1103/PhysRevD.91.019903'}])
