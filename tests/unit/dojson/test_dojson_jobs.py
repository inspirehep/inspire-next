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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.utils import clean_record


def test_date_closed_from_046__i():
    snippet = (
        '<datafield tag="046" ind1=" " ind2=" ">'
        '  <subfield code="i">2015-12-15</subfield>'
        '</datafield>'
    )  # record/1310294

    expected = '2015-12-15'
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['deadline_date']


def test_date_closed_from_046__l():
    snippet = (
        '<datafield tag="046" ind1=" " ind2=" ">'
        '  <subfield code="l">2008-02-11</subfield>'
        '</datafield>'
    )  # record/934304

    expected = '2008-02-11'
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['date_closed']


@pytest.mark.xfail(reason='incorrect structure')
def test_date_closed_from_046__i_l_an_url():
    snippet = (
        '<record>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="i">2012-06-01</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="l">http://www.pma.caltech.edu/physics-search</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/963314

    result = clean_record(jobs.do(create_record(snippet)))

    assert result['deadline_date'] == '2012-06-01'
    assert result['urls'] == [
        {
            'value': 'http://www.pma.caltech.edu/physics-search',
        },
    ]


def test_date_closed_from_046_i_l_an_email():
    snippet = (
        '<record>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="l">yejb@smu.edu</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="i">8888</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1089529

    result = clean_record(jobs.do(create_record(snippet)))

    assert result['deadline_date'] == '8888'
    assert result['reference_email'] == [
        'yejb@smu.edu',
    ]


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
    result = clean_record(jobs.do(create_record(snippet)))

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
    result = clean_record(jobs.do(create_record(snippet)))

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
    result = clean_record(jobs.do(create_record(snippet)))

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
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['contact_details']


@pytest.mark.xfail(reason='produces an array')
def test_continent_from_043__a():
    snippet = (
        '<datafield tag="043" ind1=" " ind2=" ">'
        '  <subfield code="a">Asia</subfield>'
        '</datafield>'
    )

    expected = 'Asia'
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['continent']


def test_experiments_from_693__e():
    snippet = (
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="e">CERN-LHC-ATLAS</subfield>'
        '</datafield>'
    )  # record/1471772

    expected = [
        'CERN-LHC-ATLAS',
    ]
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['experiments']


def test_experiments_from_triple_693__e():
    snippet = (
        '<record>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CERN-LHC-CMS</subfield>'
        '  </datafield>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CALICE</subfield>'
        '  </datafield>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">ILC</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1447878

    expected = [
        'CERN-LHC-CMS',
        'CALICE',
        'ILC',
    ]
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['experiments']


def test_institution_from_110__a():
    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Coll. William and Mary</subfield>'
        '</datafield>'
    )  # record/1427342

    expected = [
        {
            'curated_relation': False,
            'name': 'Coll. William and Mary',
        },
    ]
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['institution']


def test_institution_from_double_110__a():
    snippet = (
        '<record>'
        '  <datafield tag="110" ind1=" " ind2=" ">'
        '    <subfield code="a">Coll. William and Mary</subfield>'
        '  </datafield>'
        '  <datafield tag="110" ind1=" " ind2=" ">'
        '    <subfield code="a">Jefferson Lab</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1427342

    expected = [
        {
            'curated_relation': False,
            'name': 'Coll. William and Mary',
        },
        {
            'curated_relation': False,
            'name': 'Jefferson Lab',
        },
    ]
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['institution']


@pytest.mark.xfail(reason='institution has length one')
def test_institution_from_100__double_a():
    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Indiana U.</subfield>'
        '  <subfield code="a">NIST, Wash., D.C.</subfield>'
        '</datafield>'
    )  # record/1328021

    expected = [
        {
            'curated_relation': False,
            'name': 'Indiana U.',
        },
        {
            'curated_relation': False,
            'name': 'NIST, Wash., D.C.',
        },
    ]
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['institution']


# XXX: no record has a 110__z field.


def test_description_from_520__a():
    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">(1) Conduct independent research in string theory related theoretical sciences;&lt;br /> &lt;br /> (2) Advising graduate students in their research;&lt;br /> &lt;br /> (3) A very small amount of teaching of undergraduate courses.&amp;nbsp;</subfield>'
        '</datafield>'
    )  # record/1239755

    expected = '(1) Conduct independent research in string theory related theoretical sciences;<br /> <br /> (2) Advising graduate students in their research;<br /> <br /> (3) A very small amount of teaching of undergraduate courses.&nbsp;'
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['description']


def test_position_from_245__a():
    snippet = (
        '<datafield tag="245" ind1=" " ind2=" ">'
        '  <subfield code="a">Neutrino Physics</subfield>'
        '</datafield>'
    )  # record/1467312

    expected = 'Neutrino Physics'
    result = clean_record(jobs.do(create_record(snippet)))

    assert expected == result['position']


def test_ranks_from_marcxml_656_with_single_a():
    """Two ranks inside one record."""
    snippet = (
        '<record>'
        '  <datafield tag="656" ind1=" " ind2=" ">'
        '    <subfield code="a">Senior</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = clean_record(jobs.do(create_record(snippet)))

    assert result['_ranks'] == ['Senior']
    assert result['ranks'] == ['SENIOR']


def test_ranks_from_marcxml_656_with_double_a():
    """Two ranks inside one record."""
    snippet = (
        '<record>'
        '  <datafield tag="656" ind1=" " ind2=" ">'
        '    <subfield code="a">Senior</subfield>'
        '    <subfield code="a">Junior</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = clean_record(jobs.do(create_record(snippet)))

    assert result['_ranks'] == ['Senior', 'Junior']
    assert result['ranks'] == ['SENIOR', 'JUNIOR']


def test_ranks_from_marcxml_double_656():
    """Two ranks inside one record."""
    snippet = (
        '<record>'
        '  <datafield tag="656" ind1=" " ind2=" ">'
        '    <subfield code="a">Senior</subfield>'
        '  </datafield>'
        '  <datafield tag="656" ind1=" " ind2=" ">'
        '    <subfield code="a">Junior</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = clean_record(jobs.do(create_record(snippet)))

    assert result['_ranks'] == ['Senior', 'Junior']
    assert result["ranks"] == ['SENIOR', 'JUNIOR']
