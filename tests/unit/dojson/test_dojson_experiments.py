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
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.utils import strip_empty_values


def test_contact_details_from_marcxml_270_single_p_single_m():
    snippet = (
        '<record> '
        '<datafield tag="270" ind1=" " ind2=" ">'
        '<subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '<subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
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

    record = strip_empty_values(experiments.do(create_record(snippet)))
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

    record = strip_empty_values(experiments.do(create_record(snippet)))
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

    record = strip_empty_values(experiments.do(create_record(snippet)))
    assert record['contact_details'] == [{
        'name': 'Manfred Lindner',
        'email': 'lindner@mpi-hd.mpg.de'
        },
                                         {
                                             'name': 'Wynton Marsalis'
                                         }
                                         ]

def test_experiment_name_from_marcxml_119():
    """Test experiment name."""
    snippet = ( 
        '<record> '
        '<datafield tag="119" ind1=" " ind2=" "> '
        '<subfield code="a">CERN-ALPHA</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
    assert record['experiment_name'][0]['title'] == 'CERN-ALPHA'
    
def test_experiment_name_and_affiliation_from_marcxml_119():
    """Test experiment name and affiliation."""
    snippet = ( 
        '<record> '
        '<datafield tag="119" ind1=" " ind2=" "> '
        '<subfield code="a">CERN-ALPHA</subfield> '
        '<subfield code="u">CERN</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
    assert record['affiliations'][0] == 'CERN'
    assert record['experiment_name'][0]['title'] == 'CERN-ALPHA'


def test_experiment_name_and_affiliation_from_marcxml_119_two_u():
    """Test experiment name with two affiliations."""
    snippet = ( 
        '<record> '
        '<datafield tag="119" ind1=" " ind2=" "> '
        '<subfield code="a">LATTICE-UKQCD</subfield> '
        '<subfield code="u">Cambridge U.</subfield> '
        '<subfield code="u">Edinburgh U.</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
    assert record['affiliations'] == ['Cambridge U.', 'Edinburgh U.']
    assert record['experiment_name'][0]['title'] == 'LATTICE-UKQCD'


def test_titles_from_marcxml_245():
    """Test experiment title (long name)."""
    snippet = ( 
        '<record> '
        '<datafield tag="245" ind1=" " ind2=" "> '
        '<subfield code="a">The ALPHA experiment</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
    title = 'The ALPHA experiment'
    assert record['titles'][0]['title'] == title


def test_title_variants__from_marcxml_419():
    """Test experiment title variants."""
    snippet = ( 
        '<record> '
        '<datafield tag="419" ind1=" " ind2=" "> '
        '<subfield code="a">ALPHA</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
    title_variants = [{'title': 'ALPHA'}]
    assert record['title_variants'] == title_variants


def test_multiple_title_variants__from_marcxml_419():
    """Test experiment title variants."""
    snippet = ( 
        '<record> '
        '<datafield tag="419" ind1=" " ind2=" "> '
        '<subfield code="a">P-326</subfield> '
        '</datafield> '
        '<datafield tag="419" ind1=" " ind2=" "> '
        '<subfield code="a">CERN-NA-048-3</subfield> '
        '</datafield> '
        '</record>'
    )

    record = strip_empty_values(experiments.do(create_record(snippet)))
    assert record['title_variants'][0]['title'] == 'P-326'
    assert record['title_variants'][1]['title'] == 'CERN-NA-048-3'
