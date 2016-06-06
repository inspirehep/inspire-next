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

from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.utils import strip_empty_values


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
    result = strip_empty_values(experiments.do(create_record(snippet)))

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
    result = strip_empty_values(experiments.do(create_record(snippet)))

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
    result = strip_empty_values(experiments.do(create_record(snippet)))

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
    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert expected == result['contact_details']


def test_experiment_names_from_marcxml_119():
    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'CERN-ALPHA',
        },
    ]
    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert expected == result['experiment_names']


def test_experiment_names_and_affiliation_from_marcxml_119():
    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '    <subfield code="u">CERN</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert result['affiliation'][0] == 'CERN'
    assert result['experiment_names'][0]['title'] == 'CERN-ALPHA'


def test_experiment_names_and_affiliation_from_marcxml_119_two_u():
    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">LATTICE-UKQCD</subfield>'
        '    <subfield code="u">Cambridge U.</subfield>'
        '    <subfield code="u">Edinburgh U.</subfield>'
        '  </datafield>'
        '</record>'
    )

    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert result['affiliation'] == ['Cambridge U.', 'Edinburgh U.']
    assert result['experiment_names'][0]['title'] == 'LATTICE-UKQCD'


def test_titles_from_marcxml_245():
    snippet = (
        '<record>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        '    <subfield code="a">The ALPHA experiment</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'The ALPHA experiment',
        },
    ]
    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert expected == result['titles']


def test_title_variants_from_marcxml_419():
    snippet = (
        '<record>'
        '  <datafield tag="419" ind1=" " ind2=" ">'
        '    <subfield code="a">ALPHA</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'ALPHA',
        },
    ]
    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert expected == result['title_variants']


def test_multiple_title_variants_from_marcxml_419():
    snippet = (
        '<record>'
        '  <datafield tag="419" ind1=" " ind2=" ">'
        '    <subfield code="a">P-326</subfield>'
        '  </datafield>'
        '  <datafield tag="419" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-NA-048-3</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'title': 'P-326',
        },
        {
            'title': 'CERN-NA-048-3',
        },
    ]
    result = strip_empty_values(experiments.do(create_record(snippet)))

    assert expected == result['title_variants']
