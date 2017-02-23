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
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.utils import validate


def test_contact_details_from_marcxml_270_single_p_single_m():
    schema = load_schema('experiments')
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
    result = experiments.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_double_p_single_m():
    schema = load_schema('experiments')
    subschema = schema['properties']['contact_details']

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
    result = experiments.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_marcxml_270_single_p_double_m():
    schema = load_schema('experiments')
    subschema = schema['properties']['contact_details']

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
    result = experiments.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_contact_details_from_multiple_marcxml_270():
    schema = load_schema('experiments')
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
    result = experiments.do(create_record(snippet))

    assert validate(result['contact_details'], subschema) is None
    assert expected == result['contact_details']


def test_experiment_names_from_marcxml_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment_names']

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
    result = experiments.do(create_record(snippet))

    assert validate(result['experiment_names'], subschema) is None
    assert expected == result['experiment_names']


def test_experiment_names_and_affiliations_from_marcxml_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment_names']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '    <subfield code="u">CERN</subfield>'
        '    <subfield code="z">902725</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1108206

    result = experiments.do(create_record(snippet))

    assert validate(result['experiment_names'], subschema) is None
    assert result['experiment_names'] == [{'title': 'CERN-ALPHA'}]
    assert result['affiliations'] == [
        {
            'curated_relation': True,
            'name': 'CERN',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902725',
            },
        },
    ]


def test_experiment_names_and_affiliations_from_marcxml_multiple_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment_names']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">LATTICE-UKQCD</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Cambridge U.</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Edinburgh U.</subfield>'
        '    <subfield code="z">902787</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Swansea U.</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1228417

    result = experiments.do(create_record(snippet))

    assert validate(result['experiment_names'], subschema) is None
    assert result['experiment_names'] == [{'title': 'LATTICE-UKQCD'}]
    assert result['affiliations'] == [
        {
            'curated_relation': False,
            'name': 'Cambridge U.'
        },
        {
            'curated_relation': True,
            'name': 'Edinburgh U.',
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902787',
            },
        },
        {
            'curated_relation': False,
            'name': 'Swansea U.'
        }
    ]


def test_titles_from_marcxml_245():
    schema = load_schema('experiments')
    subschema = schema['properties']['titles']

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
    result = experiments.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_titles_from_419__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="419" ind1=" " ind2=" ">'
        '  <subfield code="a">ALPHA</subfield>'
        '</datafield>'
    )  # record/1108206

    expected = [
        {'title': 'ALPHA'},
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_titles_from_245__a_and_419__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['titles']

    snippet = (
        '<record>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        r'    <subfield code="a">Proposal to measure the very rare kaon decay $K^+ \to \pi^+ \nu \bar{\nu}$</subfield>'
        '  </datafield>'
        '  <datafield tag="419" ind1=" " ind2=" ">'
        '    <subfield code="a">P-326</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1275752

    expected = [
        {'title': r'Proposal to measure the very rare kaon decay $K^+ \to \pi^+ \nu \bar{\nu}$'},
        {'title': 'P-326'},
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']


def test_description_from_520__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['description']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">The Muon Accelerator Program (MAP) was created in 2010 to unify the DOE supported R&amp;D in the U.S. aimed at developing the concepts and technologies required for Muon Colliders and Neutrino Factories. These muon based facilities have the potential to discover and explore new exciting fundamental physics, but will require the development of demanding technologies and innovative concepts. The MAP aspires to prove the feasibility of a Muon Collider within a few years, and to make significant contributions to the international effort devoted to developing Neutrino Factories. MAP was formally approved on March 18, 2011.</subfield>'
        '</datafield>'
    )  # record/1108188

    expected = [
        'The Muon Accelerator Program (MAP) was created in 2010 to unify the DOE supported R&D in the U.S. aimed at developing the concepts and technologies required for Muon Colliders and Neutrino Factories. These muon based facilities have the potential to discover and explore new exciting fundamental physics, but will require the development of demanding technologies and innovative concepts. The MAP aspires to prove the feasibility of a Muon Collider within a few years, and to make significant contributions to the international effort devoted to developing Neutrino Factories. MAP was formally approved on March 18, 2011.'
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['description'], subschema) is None
    assert expected == result['description']


def test_description_from_multiple_520__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['description']

    snippet = (
        '<record>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">DAMA is an observatory for rare processes which develops and uses several low-background set-ups at the Gran Sasso National Laboratory of the I.N.F.N. (LNGS). The main experimental set-ups are: i) DAMA/NaI (about 100 kg of highly radiopure NaI(Tl)), which completed its data taking on July 2002</subfield>'
        '  </datafield>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">ii) DAMA/LXe (about 6.5 kg liquid Kr-free Xenon enriched either in 129Xe or in 136Xe)</subfield>'
        '  </datafield>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">iii) DAMA/R&amp;D, devoted to tests on prototypes and to small scale experiments, mainly on the investigations of double beta decay modes in various isotopes. iv) the second generation DAMA/LIBRA set-up (about 250 kg highly radiopure NaI(Tl)) in operation since March 2003</subfield>'
        '  </datafield>'
        '  <datafield tag="520" ind1=" " ind2=" ">'
        '    <subfield code="a">v) the low background DAMA/Ge detector mainly devoted to sample measurements: in some measurements on rare processes the low-background Germanium detectors of the LNGS facility are also used. Moreover, a third generation R&amp;D is in progress towards a possible 1 ton set-up, DAMA proposed in 1996. In particular, the DAMA/NaI and the DAMA/LIBRA set-ups have investigated the presence of Dark Matter particles in the galactic halo by exploiting the Dark Matter annual modulation signature.</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1110568

    expected = [
        'DAMA is an observatory for rare processes which develops and uses several low-background set-ups at the Gran Sasso National Laboratory of the I.N.F.N. (LNGS). The main experimental set-ups are: i) DAMA/NaI (about 100 kg of highly radiopure NaI(Tl)), which completed its data taking on July 2002',
        'ii) DAMA/LXe (about 6.5 kg liquid Kr-free Xenon enriched either in 129Xe or in 136Xe)',
        'iii) DAMA/R&D, devoted to tests on prototypes and to small scale experiments, mainly on the investigations of double beta decay modes in various isotopes. iv) the second generation DAMA/LIBRA set-up (about 250 kg highly radiopure NaI(Tl)) in operation since March 2003',
        'v) the low background DAMA/Ge detector mainly devoted to sample measurements: in some measurements on rare processes the low-background Germanium detectors of the LNGS facility are also used. Moreover, a third generation R&D is in progress towards a possible 1 ton set-up, DAMA proposed in 1996. In particular, the DAMA/NaI and the DAMA/LIBRA set-ups have investigated the presence of Dark Matter particles in the galactic halo by exploiting the Dark Matter annual modulation signature.',
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['description'], subschema) is None
    assert expected == result['description']


def test_spokespersons_from_702__a_i_z():
    schema = load_schema('experiments')
    subschema = schema['properties']['spokespersons']

    snippet = (
        '<datafield tag="702" ind1=" " ind2=" ">'
        '  <subfield code="a">Hogan, Craig J.</subfield>'
        '  <subfield code="i">INSPIRE-00090662</subfield>'
        '  <subfield code="z">Current</subfield>'
        '</datafield>'
    )  # record/1108189

    expected = [
        {
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00090662',
                },
            ],
            'name': 'Hogan, Craig J.',
            'current': True,
            'curated_relation': False,
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['spokespersons'], subschema) is None
    assert expected == result['spokespersons']


def test_spokespersons_from_double_702__a_i():
    schema = load_schema('experiments')
    subschema = schema['properties']['spokespersons']

    snippet = (
        '<record>'
        '  <datafield tag="702" ind1=" " ind2=" ">'
        '    <subfield code="a">Feldman, Gary</subfield>'
        '    <subfield code="i">INSPIRE-00080677</subfield>'
        '    <subfield code="x">1010209</subfield>'
        '  </datafield>'
        '  <datafield tag="702" ind1=" " ind2=" ">'
        '    <subfield code="a">Messier, Mark</subfield>'
        '    <subfield code="i">INSPIRE-00107105</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1402897

    expected = [
        {
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00080677',
                },
            ],
            'name': 'Feldman, Gary',
            'record': {'$ref': 'http://localhost:5000/api/authors/1010209'},
            'curated_relation': True,
        },
        {
            'ids': [
                {
                    'schema': 'INSPIRE ID',
                    'value': 'INSPIRE-00107105',
                },
            ],
            'name': 'Messier, Mark',
            'curated_relation': False,
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['spokespersons'], subschema) is None
    assert expected == result['spokespersons']


def test_collaboration_from_710__g():
    schema = load_schema('experiments')
    subschema = schema['properties']['collaboration']

    snippet = (
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">DarkSide</subfield>'
        '</datafield>'
    )  # record/1108199

    result = experiments.do(create_record(snippet))

    assert validate(result['collaboration'], subschema) is None
    assert result['collaboration'] == 'DarkSide'
    assert 'collaboration_alternative_names' not in result


def test_collaboration_from_double_710__g():
    schema = load_schema('experiments')
    subschema = schema['properties']['collaboration']

    snippet = (
        '<record>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">MiniBooNE</subfield>'
        '  </datafield>'
        '  <datafield tag="710" ind1=" " ind2=" ">'
        '    <subfield code="g">BooNE</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1110641

    result = experiments.do(create_record(snippet))

    assert validate(result['collaboration'], subschema) is None
    assert result['collaboration'] == 'BooNE'
    assert result['collaboration_alternative_names'] == ['MiniBooNE']


def test_related_experiments_from_510__a_w_0():
    schema = load_schema('experiments')
    subschema = schema['properties']['related_experiments']

    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="0">1262631</subfield>'
        '  <subfield code="a">LZ</subfield>'
        '  <subfield code="w">b</subfield>'
        '</datafield>'
    )  # record/1108192

    expected = [
        {
            'name': 'LZ',
            'record': {'$ref': 'http://localhost:5000/api/experiments/1262631'},
            'relation': 'successor',
            'curated_relation': True,
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['related_experiments'], subschema) is None
    assert expected == result['related_experiments']


def test_related_experiments_from_double_510__a_w_0():
    schema = load_schema('experiments')
    subschema = schema['properties']['related_experiments']

    snippet = (
        '<record>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">1108293</subfield>'
        '    <subfield code="a">XENON</subfield>'
        '    <subfield code="w">a</subfield>'
        '  </datafield>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">1386527</subfield>'
        '    <subfield code="a">XENON100</subfield>'
        '    <subfield code="w">a</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1386519

    expected = [
        {
            'name': 'XENON',
            'record': {'$ref': 'http://localhost:5000/api/experiments/1108293'},
            'relation': 'predecessor',
            'curated_relation': True,
        },
        {
            'name': 'XENON100',
            'record': {'$ref': 'http://localhost:5000/api/experiments/1386527'},
            'relation': 'predecessor',
            'curated_relation': True,
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['related_experiments'], subschema) is None
    assert expected == result['related_experiments']


def test_date_started_from_046__q_s_and_046__r():
    schema = load_schema('experiments')
    subschema = schema['properties']['date_started']

    snippet = (
        '<record>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="q">2009-08-19</subfield>'
        '    <subfield code="s">2009-11-30</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="r">2009-10-08</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1318099

    expected = '2009-11-30'
    result = experiments.do(create_record(snippet))

    assert validate(result['date_started'], subschema) is None
    assert expected == result['date_started']


def test_date_started_from_046__q_and_046__r_and_046__x():
    snippet = (
        '<record>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="q">2010</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="r">2011-03-18</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="x">yes</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1108188

    result = experiments.do(create_record(snippet))

    assert 'date_started' not in result


def test_date_started_and_date_completed_from_046():
    schema = load_schema('experiments')
    subschema_date_started = schema['properties']['date_started']
    subschema_date_completed = schema['properties']['date_started']

    snippet = (
        '<record>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="s">1996</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="t">2002</subfield>'
        '  </datafield>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="x">yes</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1108324

    result = experiments.do(create_record(snippet))

    assert validate(result['date_started'], subschema_date_started) is None
    assert validate(result['date_completed'], subschema_date_completed) is None
    assert result['date_started'] == '1996'
    assert result['date_completed'] == '2002'


def test_accelerator_from_693__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['accelerator']

    snippet = (
        '<datafield tag="693" ind1=" " ind2=" ">'
        '  <subfield code="a">AD</subfield>'
        '</datafield>'
    )  # record/1108206

    expected = 'AD'
    result = experiments.do(create_record(snippet))

    assert validate(result['accelerator'], subschema) is None
    assert expected == result['accelerator']
