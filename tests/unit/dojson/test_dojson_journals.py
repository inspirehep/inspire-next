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
from inspirehep.dojson.journals import journals
from inspirehep.dojson.utils import strip_empty_values


def test_issn_from_marcxml_022_with_a():
    """Test simple ISSN without medium."""
    snippet = (
            '<record> '
            '<datafield tag="022" ind1=" " ind2=" "> '
            '<subfield code="a">2213-1337</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert record['issn'][0]['value'] == '2213-1337'


def test_issn_from_marcxml_022_with_a_and_b():
    """Test ISSN with medium normalization."""
    snippet = (
            '<record> '
            '<datafield tag="022" ind1=" " ind2=" "> '
            '<subfield code="a">2213-1337</subfield> '
            '<subfield code="b">Print</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert record['issn'][0]['value'] == '2213-1337'
    assert record['issn'][0]['medium'] == 'print'


def test_issn_from_marcxml_022_with_a_and_b_and_comment():
    """Test ISSN with medium normalization. The original 'b' value
    will be stored in 'comment'.
    """
    snippet = (
            '<record> '
            '<datafield tag="022" ind1=" " ind2=" "> '
            '<subfield code="a">2213-1337</subfield> '
            '<subfield code="b">ebook</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert record['issn'][0]['value'] == '2213-1337'
    assert record['issn'][0]['medium'] == 'online'
    assert record['issn'][0]['comment'] == 'ebook'


def test_issn_from_marcxml_022_with_b_no_a():
    """Test ISSN in wrong subfield."""
    snippet = (
            '<record> '
            '<datafield tag="022" ind1=" " ind2=" "> '
            '<subfield code="b">9780486632827</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert 'issn' not in record


def test_multiple_issn_from_marcxml_022():
    """Test multiple ISSNs."""
    snippet = (
            '<record> '
            '<datafield tag="022" ind1=" " ind2=" "> '
            '<subfield code="a">2349-2716</subfield> '
            '<subfield code="b">Online</subfield> '
            '</datafield> '
            '<datafield tag="022" ind1=" " ind2=" "> '
            '<subfield code="a">2349-6088</subfield> '
            '<subfield code="b">Print</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert record['issn'][0]['value'] == '2349-2716'
    assert record['issn'][0]['medium'] == 'online'
    assert record['issn'][1]['value'] == '2349-6088'
    assert record['issn'][1]['medium'] == 'print'


def test_coden_from_marcxml_030():
    """Test coden."""
    snippet = (
            '<datafield tag="030" ind1=" " ind2=" "> '
            '<subfield code="2">CODEN</subfield> '
            '<subfield code="a">PRSTA</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert record['coden'][0] == 'PRSTA'


def test_publisher_from_marcxml_643():
    """Test publisher."""
    snippet = (
            '<datafield tag="643" ind1=" " ind2=" "> '
            '<subfield code="b">APS</subfield> '
            '</datafield> '
            '</record>'
        )

    record = strip_empty_values(journals.do(create_record(snippet)))
    assert record['publisher'][0] == 'APS'


def test_titles_from_marcxml_130_with_single_a():
    """Test title."""
    snippet = (
        '<record> '
        '<datafield tag="130" ind1=" " ind2=" "> '
        '<subfield code="a">Physical Review Special Topics - Accelerators and Beams</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(journals.do(create_record(snippet)))
    title = 'Physical Review Special Topics - Accelerators and Beams'
    assert record['titles'][0]['title'] == title


def test_titles_from_marcxml_130_with_a_and_b():
    """Test title and subtitle."""
    snippet = (
        '<record> '
        '<datafield tag="130" ind1=" " ind2=" "> '
        '<subfield code="a">Humana Mente</subfield> '
        '<subfield code="b">Journal of Philosophical Studies</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(journals.do(create_record(snippet)))
    title = 'Humana Mente'
    subtitle = 'Journal of Philosophical Studies'
    assert record['titles'][0]['title'] == title
    assert record['titles'][0]['subtitle'] == subtitle
    


def test_short_titles_from_marcxml_711():
    """Test short title."""
    snippet = (
        '<record> '
        '<datafield tag="711" ind1=" " ind2=" "> '
        '<subfield code="a">Phys.Rev.ST Accel.Beams</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(journals.do(create_record(snippet)))
    title = 'Phys.Rev.ST Accel.Beams'
    assert record['short_titles'][0]['title'] == title


def test_title_variants_from_marcxml_730():
    """Test single title variant."""
    snippet = (
        '<record> '
        '<datafield tag="730" ind1=" " ind2=" "> '
        '<subfield code="a">PHYSICAL REVIEW SPECIAL TOPICS ACCELERATORS AND BEAMS</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(journals.do(create_record(snippet)))
    title = 'PHYSICAL REVIEW SPECIAL TOPICS ACCELERATORS AND BEAMS'
    assert record['title_variants'][0]['title'] == title


def test_multiple_title_variants_from_marcxml_730():
    """Test two title variants."""
    snippet = (
        '<record> '
        '<datafield tag="730" ind1=" " ind2=" "> '
        '<subfield code="a">PHYS REV SPECIAL TOPICS ACCELERATORS BEAMS</subfield> '
        '</datafield> '
        '<datafield tag="730" ind1=" " ind2=" "> '
        '<subfield code="a">PHYSICS REVIEW ST ACCEL BEAMS</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(journals.do(create_record(snippet)))
    title0 = 'PHYS REV SPECIAL TOPICS ACCELERATORS BEAMS'
    title1 = 'PHYSICS REVIEW ST ACCEL BEAMS'
    assert record['title_variants'][0]['title'] == title0
    assert record['title_variants'][1]['title'] == title1
    