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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

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


def test_contact_details_from_marcxml_270_single_p_single_m():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '<subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(jobs.do(create_record(snippet)))
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

    record = strip_empty_values(jobs.do(create_record(snippet)))
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

    record = strip_empty_values(jobs.do(create_record(snippet)))
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

    record = strip_empty_values(jobs.do(create_record(snippet)))
    assert record['contact_details'] == [{
        'name': 'Manfred Lindner',
        'email': 'lindner@mpi-hd.mpg.de'
        },
                                         {
                                             'name': 'Wynton Marsalis'
                                         }
                                         ]
