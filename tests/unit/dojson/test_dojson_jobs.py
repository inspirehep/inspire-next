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
from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.utils import strip_empty_values

def test_ranks_from_marcxml_656_with_single_a():
    """Two ranks inside one record."""
    snippet = (
        '<record> '
        '<datafield tag="656" ind1=" " ind2=" ">'
        '<subfield code="a">Senior</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(jobs.do(create_record(snippet)))
    assert record['_ranks'] == ['Senior']
    assert record["ranks"] == ['SENIOR']

def test_ranks_from_marcxml_656_with_double_a():
    """Two ranks inside one record."""
    snippet = (
        '<record> '
        '<datafield tag="656" ind1=" " ind2=" ">'
        '<subfield code="a">Senior</subfield>'
        '<subfield code="a">Junior</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(jobs.do(create_record(snippet)))
    assert record['_ranks'] == ['Senior', 'Junior']
    assert record["ranks"] == ['SENIOR', 'JUNIOR']


def test_ranks_from_marcxml_double_656():
    """Two ranks inside one record."""
    snippet = (
        '<record> '
        '<datafield tag="656" ind1=" " ind2=" ">'
        '<subfield code="a">Senior</subfield>'
        '</datafield>'
        '<datafield tag="656" ind1=" " ind2=" ">'
        '<subfield code="a">Junior</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(jobs.do(create_record(snippet)))
    assert record['_ranks'] == ['Senior', 'Junior']
    assert record["ranks"] == ['SENIOR', 'JUNIOR']
