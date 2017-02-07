# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from inspire_schemas.utils import load_schema
from inspirehep.dojson.jobs import jobs
from inspirehep.dojson.utils import validate


def test_deadline_date_from_046__i():
    schema = load_schema('jobs')
    subschema = schema['properties']['deadline_date']

    snippet = (
        '<datafield tag="046" ind1=" " ind2=" ">'
        '  <subfield code="i">2015-12-15</subfield>'
        '</datafield>'
    )  # record/1310294

    expected = '2015-12-15'
    result = jobs.do(create_record(snippet))

    assert validate(result['deadline_date'], subschema) is None
    assert expected == result['deadline_date']


def test_closed_date_from_046__l():
    schema = load_schema('jobs')
    subschema = schema['properties']['closed_date']

    snippet = (
        '<datafield tag="046" ind1=" " ind2=" ">'
        '  <subfield code="l">2008-02-11</subfield>'
        '</datafield>'
    )  # record/934304

    expected = '2008-02-11'
    result = jobs.do(create_record(snippet))

    assert validate(result['closed_date'], subschema) is None
    assert expected == result['closed_date']


def test_date_closed_from_046__i_and_046__l_an_url():
    schema = load_schema('jobs')
    subschema_deadline_date = schema['properties']['deadline_date']
    subschema_urls = schema['properties']['urls']

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

    expected_deadline_date = '2012-06-01'
    expected_urls = [
        {'value': 'http://www.pma.caltech.edu/physics-search'},
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['deadline_date'], subschema_deadline_date) is None
    assert expected_deadline_date == result['deadline_date']

    assert validate(result['urls'], subschema_urls) is None
    assert expected_urls == result['urls']


def test_date_closed_from_046__i_and_046__l_an_email():
    schema = load_schema('jobs')
    subschema_deadline_date = schema['properties']['deadline_date']
    subschema_reference_email = schema['properties']['reference_email']

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

    expected_deadline_date = '8888'
    expected_reference_email = ['yejb@smu.edu']
    result = jobs.do(create_record(snippet))

    assert validate(result['deadline_date'], subschema_deadline_date) is None
    assert expected_deadline_date == result['deadline_date']

    assert validate(result['reference_email'], subschema_reference_email) is None
    assert expected_reference_email == result['reference_email']


def test_contact_details_from_marcxml_270_single_p_single_m():
    schema = load_schema('jobs')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '  <subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'name': 'Manfred Lindner',
            'email': 'lindner@mpi-hd.mpg.de',
        },
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_double_p_single_m():
    schema = load_schema('jobs')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '  <subfield code="p">Manfred Lindner</subfield>'
        '  <subfield code="p">Boogeyman</subfield>'
        '</datafield>'
    )

    expected = [
        {'email': 'lindner@mpi-hd.mpg.de'},
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_single_p_double_m():
    schema = load_schema('jobs')
    subschema = schema['properties']['contact_details']

    snippet = (
        '<datafield tag="270" ind1=" " ind2=" ">'
        '  <subfield code="m">lindner@mpi-hd.mpg.de</subfield>'
        '  <subfield code="m">lindner@ecmrecords.com</subfield>'
        '  <subfield code="p">Manfred Lindner</subfield>'
        '</datafield>'
    )

    expected = [
        {'name': 'Manfred Lindner'},
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_multiple_marcxml_270():
    schema = load_schema('jobs')
    subschema = schema['properties']['contact_details']

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
    result = jobs.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_regions_from_043__a():
    schema = load_schema('jobs')
    subschema = schema['properties']['regions']

    snippet = (
        '<datafield tag="043" ind1=" " ind2=" ">'
        '  <subfield code="a">Asia</subfield>'
        '</datafield>'
    )

    expected = ['Asia']
    result = jobs.do(create_record(snippet))

    assert validate(result['regions'], subschema) is None
    assert expected == result['regions']


def test_regions_from_043__a_corrects_misspellings():
    schema = load_schema('jobs')
    subschema = schema['properties']['regions']

    snippet = (
        '<datafield tag="043" ind1=" " ind2=" ">'
        '  <subfield code="a">United States</subfield>'
        '</datafield>'
    )

    expected = ['North America']
    result = jobs.do(create_record(snippet))

    assert validate(result['regions'], subschema) is None
    assert expected == result['regions']


def test_regions_from_043__a_splits_on_commas():
    schema = load_schema('jobs')
    subschema = schema['properties']['regions']

    snippet = (
        '<datafield tag="043" ind1=" " ind2=" ">'
        '  <subfield code="a">Asia, North America</subfield>'
        '</datafield>'
    )

    expected = ['Asia', 'North America']
    result = jobs.do(create_record(snippet))

    assert validate(result['regions'], subschema) is None
    assert expected == result['regions']


def test_experiments_from_693__e():
    schema = load_schema('jobs')
    subschema = schema['properties']['experiments']

    snippet = (
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="e">ALIGO</subfield>'
        '</datafield>'
    )  # record/1375852

    expected = [
        {
            'curated_relation': False,
            'name': 'ALIGO',
        },
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['experiments'], subschema) is None
    assert expected == result['experiments']


def test_experiments_from_693__e__0():
    schema = load_schema('jobs')
    subschema = schema['properties']['experiments']

    snippet = (
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="e">CERN-LHC-ATLAS</subfield>'
        '  <subfield code="0">1108541</subfield>'
        '</datafield>'
    )  # record/1332138

    expected = [
        {
            'curated_relation': True,
            'name': 'CERN-LHC-ATLAS',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108541',
            },
        },
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['experiments'], subschema) is None
    assert expected == result['experiments']


def test_experiments_from_693__e__0_and_e():
    schema = load_schema('jobs')
    subschema = schema['properties']['experiments']

    snippet = (
        '<record>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CERN-LHC-ATLAS</subfield>'
        '    <subfield code="0">1108541</subfield>'
        '  </datafield>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">IHEP-CEPC</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1393583/export/xme

    expected = [
        {
            'curated_relation': True,
            'name': 'CERN-LHC-ATLAS',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108541',
            },
        },
        {
            'curated_relation': False,
            'name': 'IHEP-CEPC'
        }
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['experiments'], subschema) is None
    assert expected == result['experiments']


def test_experiments_from_triple_693__e__0():
    schema = load_schema('jobs')
    subschema = schema['properties']['experiments']

    snippet = (
        '<record>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CERN-NA-049</subfield>'
        '    <subfield code="0">1110308</subfield>'
        '  </datafield>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CERN-NA-061</subfield>'
        '    <subfield code="0">1108234</subfield>'
        '  </datafield>'
        '  <datafield tag="693" ind1=" " ind2=" ">'
        '    <subfield code="e">CERN-LHC-ALICE</subfield>'
        '    <subfield code="0">1110642</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1469159

    expected = [
        {
            'curated_relation': True,
            'name': 'CERN-NA-049',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110308',
            },
        },
        {
            'curated_relation': True,
            'name': 'CERN-NA-061',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108234',
            },
        },
        {
            'curated_relation': True,
            'name': 'CERN-LHC-ALICE',
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1110642',
            },
        }
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['experiments'], subschema) is None
    assert expected == result['experiments']


def test_institutions_from_110__a():
    schema = load_schema('jobs')
    subschema = schema['properties']['institutions']

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
    result = jobs.do(create_record(snippet))

    assert validate(result['institutions'], subschema) is None
    assert expected == result['institutions']


def test_institutions_from_double_110__a():
    schema = load_schema('jobs')
    subschema = schema['properties']['institutions']

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
    result = jobs.do(create_record(snippet))

    assert validate(result['institutions'], subschema) is None
    assert expected == result['institutions']


def test_institutions_from_110__double_a_z():
    schema = load_schema('jobs')
    subschema = schema['properties']['institutions']

    snippet = (
        '<datafield tag="110" ind1=" " ind2=" ">'
        '  <subfield code="a">Indiana U.</subfield>'
        '  <subfield code="a">NIST, Wash., D.C.</subfield>'
        '  <subfield code="z">902874</subfield>'
        '  <subfield code="z">903056</subfield>'
        '</datafield>'
    )  # record/1328021/export/xme

    expected = [
        {
            'curated_relation': True,
            'name': 'Indiana U.',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902874',
            },
        },
        {
            'curated_relation': True,
            'name': 'NIST, Wash., D.C.',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/903056',
            },
        },
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['institutions'], subschema) is None
    assert expected == result['institutions']


def test_description_from_520__a():
    schema = load_schema('jobs')
    subschema = schema['properties']['description']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">(1) Conduct independent research in string theory related theoretical sciences;&lt;br /> &lt;br /> (2) Advising graduate students in their research;&lt;br /> &lt;br /> (3) A very small amount of teaching of undergraduate courses.&amp;nbsp;</subfield>'
        '</datafield>'
    )  # record/1239755

    expected = '(1) Conduct independent research in string theory related theoretical sciences;<br /> <br /> (2) Advising graduate students in their research;<br /> <br /> (3) A very small amount of teaching of undergraduate courses.&nbsp;'
    result = jobs.do(create_record(snippet))

    assert validate(result['description'], subschema) is None
    assert expected == result['description']


def test_position_from_245__a():
    schema = load_schema('jobs')
    subschema = schema['properties']['position']

    snippet = (
        '<datafield tag="245" ind1=" " ind2=" ">'
        '  <subfield code="a">Neutrino Physics</subfield>'
        '</datafield>'
    )  # record/1467312

    expected = 'Neutrino Physics'
    result = jobs.do(create_record(snippet))

    assert validate(result['position'], subschema) is None
    assert expected == result['position']


def test_ranks_from_marcxml_656_with_single_a():
    schema = load_schema('jobs')
    subschema = schema['properties']['ranks']

    snippet = (
        '<datafield tag="656" ind1=" " ind2=" ">'
        '  <subfield code="a">Senior</subfield>'
        '</datafield>'
    )

    result = jobs.do(create_record(snippet))

    assert validate(result['ranks'], subschema) is None
    assert result['ranks'] == ['SENIOR']


def test_ranks_from_marcxml_656_with_double_a():
    schema = load_schema('jobs')
    subschema = schema['properties']['ranks']

    snippet = (
        '<datafield tag="656" ind1=" " ind2=" ">'
        '  <subfield code="a">Senior</subfield>'
        '  <subfield code="a">Junior</subfield>'
        '</datafield>'
    )

    expected = [
        'SENIOR',
        'JUNIOR',
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['ranks'], subschema) is None
    assert expected == result['ranks']


def test_ranks_from_marcxml_double_656():
    schema = load_schema('jobs')
    subschema = schema['properties']['ranks']

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

    expected = [
        'SENIOR',
        'JUNIOR',
    ]
    result = jobs.do(create_record(snippet))

    assert validate(result['ranks'], subschema) is None
    assert expected == result['ranks']
