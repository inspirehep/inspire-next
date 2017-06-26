# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.utils import validate


def test_dates_from_046__q_s_and_046__r():
    schema = load_schema('experiments')
    date_proposed_schema = schema['properties']['date_proposed']
    date_approved_schema = schema['properties']['date_approved']
    date_started_schema = schema['properties']['date_started']

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

    expected_date_proposed = '2009-08-19'
    expected_date_approved = '2009-10-08'
    expected_date_started = '2009-11-30'
    result = experiments.do(create_record(snippet))

    assert validate(result['date_proposed'], date_proposed_schema) is None
    assert expected_date_proposed == result['date_proposed']

    assert validate(result['date_approved'], date_approved_schema) is None
    assert expected_date_approved == result['date_approved']

    assert validate(result['date_started'], date_started_schema) is None
    assert expected_date_started == result['date_started']


def test_dates_from_046__q_and_046__r_and_046__x():
    schema = load_schema('experiments')
    date_proposed_schema = schema['properties']['date_proposed']
    date_approved_schema = schema['properties']['date_approved']

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

    expected_date_proposed = '2010'
    expected_date_approved = '2011-03-18'
    result = experiments.do(create_record(snippet))

    assert validate(result['date_proposed'], date_proposed_schema) is None
    assert expected_date_proposed == result['date_proposed']

    assert validate(result['date_approved'], date_approved_schema) is None
    assert expected_date_approved == result['date_approved']


def test_dates_from_046__s_and_046__t_and_046__x():
    schema = load_schema('experiments')
    date_started_schema = schema['properties']['date_started']
    date_completed_schema = schema['properties']['date_completed']

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

    expected_date_started = '1996'
    expected_date_completed = '2002'
    result = experiments.do(create_record(snippet))

    assert validate(result['date_started'], date_started_schema) is None
    assert expected_date_started == result['date_started']

    assert validate(result['date_completed'], date_completed_schema) is None
    assert expected_date_completed == result['date_completed']


def test_experiment_and_institutions_from_119__a_u_z():
    schema = load_schema('experiments')
    experiment_schema = schema['properties']['experiment']
    institutions_schema = schema['properties']['institutions']

    snippet = (
        '<datafield tag="119" ind1=" " ind2=" ">'
        '  <subfield code="a">CERN-ALPHA</subfield>'
        '  <subfield code="u">CERN</subfield>'
        '  <subfield code="z">902725</subfield>'
        '</datafield>'
    )  # record/1108206

    expected_experiment = {'legacy_name': 'CERN-ALPHA'}
    expected_institutions = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902725',
            },
            'value': 'CERN',
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['experiment'], experiment_schema) is None
    assert expected_experiment == result['experiment']

    assert validate(result['institutions'], institutions_schema) is None
    assert expected_institutions == result['institutions']


def test_experiment_and_institutions_from_119__a_and_multiple_119__u_z():
    schema = load_schema('experiments')
    experiment_schema = schema['properties']['experiment']
    institutions_schema = schema['properties']['institutions']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">LATTICE-UKQCD</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Cambridge U.</subfield>'
        '    <subfield code="z">902712</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Edinburgh U.</subfield>'
        '    <subfield code="z">902787</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Glasgow U.</subfield>'
        '    <subfield code="z">902823</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Liverpool U.</subfield>'
        '    <subfield code="z">902964</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Oxford U.</subfield>'
        '    <subfield code="z">903112</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Plymouth U.</subfield>'
        '    <subfield code="z">905043</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Southampton U.</subfield>'
        '    <subfield code="z">903212</subfield>'
        '  </datafield>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="u">Swansea U.</subfield>'
        '    <subfield code="z">903240</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1228417

    expected_experiment = {'legacy_name': 'LATTICE-UKQCD'}
    expected_institutions = [
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902712',
            },
            'value': 'Cambridge U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902787',
            },
            'value': 'Edinburgh U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902823',
            },
            'value': 'Glasgow U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/902964',
            },
            'value': 'Liverpool U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/903112',
            },
            'value': 'Oxford U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/905043',
            },
            'value': 'Plymouth U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/903212',
            },
            'value': 'Southampton U.',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/institutions/903240',
            },
            'value': 'Swansea U.',
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['experiment'], experiment_schema) is None
    assert expected_experiment == result['experiment']

    assert validate(result['institutions'], institutions_schema) is None
    assert expected_institutions == result['institutions']


def test_long_name_from_245__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['long_name']

    snippet = (
        '<datafield tag="245" ind1=" " ind2=" ">'
        '  <subfield code="a">The ALPHA experiment</subfield>'
        '</datafield>'
    )  # record/1108206

    expected = 'The ALPHA experiment'
    result = experiments.do(create_record(snippet))

    assert validate(result['long_name'], subschema) is None
    assert expected == result['long_name']


def test_inspire_classification_from_372__a_9():
    schema = load_schema('experiments')
    subschema = schema['properties']['inspire_classification']

    snippet = (
        '<datafield tag="372" ind1=" " ind2=" ">'
        '  <subfield code="9">INSPIRE</subfield>'
        '  <subfield code="a">5.3</subfield>'
        '</datafield>'
    )  # record/1110577

    expected = [
        '5.3',
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['inspire_classification'], subschema) is None
    assert expected == result['inspire_classification']


def test_inspire_classification_from_372__a_ignores_non_numerical_values():
    snippet = (
        '<datafield tag="372" ind1=" " ind2=" ">'
        '  <subfield code="a">ATLAS</subfield>'
        '</datafield>'
    )  # record/1108515

    result = experiments.do(create_record(snippet))

    assert 'inspire_classification' not in result


def test_name_variants_from_419__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['name_variants']

    snippet = (
        '<datafield tag="419" ind1=" " ind2=" ">'
        '  <subfield code="a">ALPHA</subfield>'
        '</datafield>'
    )  # record/1108206

    expected = [
        'ALPHA',
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['name_variants'], subschema) is None
    assert expected == result['name_variants']


def test_long_name_and_name_variants_from_245__a_and_419__a():
    schema = load_schema('experiments')
    long_name_schema = schema['properties']['long_name']
    name_variants_schema = schema['properties']['name_variants']

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

    expected_long_name = r'Proposal to measure the very rare kaon decay $K^+ \to \pi^+ \nu \bar{\nu}$'
    expected_name_variants = [
        'P-326',
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['long_name'], long_name_schema) is None
    assert expected_long_name == result['long_name']

    assert validate(result['name_variants'], name_variants_schema) is None
    assert expected_name_variants == result['name_variants']


def test_description_from_520__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['description']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">The Muon Accelerator Program (MAP) was created in 2010 to unify the DOE supported R&amp;D in the U.S. aimed at developing the concepts and technologies required for Muon Colliders and Neutrino Factories. These muon based facilities have the potential to discover and explore new exciting fundamental physics, but will require the development of demanding technologies and innovative concepts. The MAP aspires to prove the feasibility of a Muon Collider within a few years, and to make significant contributions to the international effort devoted to developing Neutrino Factories. MAP was formally approved on March 18, 2011.</subfield>'
        '</datafield>'
    )  # record/1108188

    expected = (
        'The Muon Accelerator Program (MAP) was created in 2010 to unify the DOE supported R&D in the U.S. aimed at developing the concepts and technologies required for Muon Colliders and Neutrino Factories. These muon based facilities have the potential to discover and explore new exciting fundamental physics, but will require the development of demanding technologies and innovative concepts. The MAP aspires to prove the feasibility of a Muon Collider within a few years, and to make significant contributions to the international effort devoted to developing Neutrino Factories. MAP was formally approved on March 18, 2011.'
    )

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

    expected = (
        'DAMA is an observatory for rare processes which develops and uses several low-background set-ups at the Gran Sasso National Laboratory of the I.N.F.N. (LNGS). The main experimental set-ups are: i) DAMA/NaI (about 100 kg of highly radiopure NaI(Tl)), which completed its data taking on July 2002\n'
        'ii) DAMA/LXe (about 6.5 kg liquid Kr-free Xenon enriched either in 129Xe or in 136Xe)\n'
        'iii) DAMA/R&D, devoted to tests on prototypes and to small scale experiments, mainly on the investigations of double beta decay modes in various isotopes. iv) the second generation DAMA/LIBRA set-up (about 250 kg highly radiopure NaI(Tl)) in operation since March 2003\n'
        'v) the low background DAMA/Ge detector mainly devoted to sample measurements: in some measurements on rare processes the low-background Germanium detectors of the LNGS facility are also used. Moreover, a third generation R&D is in progress towards a possible 1 ton set-up, DAMA proposed in 1996. In particular, the DAMA/NaI and the DAMA/LIBRA set-ups have investigated the presence of Dark Matter particles in the galactic halo by exploiting the Dark Matter annual modulation signature.'
    )
    result = experiments.do(create_record(snippet))

    assert validate(result['description'], subschema) is None
    assert expected == result['description']


def test_related_records_from_double_510__a_w_0_accepts_predecessors():
    schema = load_schema('experiments')
    subschema = schema['properties']['related_records']

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
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1108293',
            },
            'relation': 'predecessor',
        },
        {
            'curated_relation': True,
            'record': {
                '$ref': 'http://localhost:5000/api/experiments/1386527',
            },
            'relation': 'predecessor',
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']


def test_related_records_from_510__a_w_0_discards_successors():
    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="0">1262631</subfield>'
        '  <subfield code="a">LZ</subfield>'
        '  <subfield code="w">b</subfield>'
        '</datafield>'
    )  # record/1108192

    result = experiments.do(create_record(snippet))

    assert 'related_records' not in result


def test_collaboration_from_710__g_0():
    schema = load_schema('experiments')
    subschema = schema['properties']['collaboration']

    snippet = (
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">DarkSide</subfield>'
        '  <subfield code="0">1108199</subfield>'
        '</datafield>'
    )  # record/1108199

    expected = {
        'curated_relation': True,
        'record': {
            '$ref': 'http://localhost:5000/api/experiments/1108199',
        },
        'value': 'DarkSide',
    }
    result = experiments.do(create_record(snippet))

    assert validate(result['collaboration'], subschema) is None
    assert expected == result['collaboration']


def test_core_from_double_980__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['core']

    snippet = (
        '<record>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">CORE</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">EXPERIMENT</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1332131

    expected = True
    result = experiments.do(create_record(snippet))

    assert validate(result['core'], subschema) is None
    assert expected == result['core']


def test_core_and_deleted_from_multiple_980__a():
    schema = load_schema('experiments')
    core_schema = schema['properties']['core']
    deleted_schema = schema['properties']['deleted']

    snippet = (
        '<record>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">CORE</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">EXPERIMENT</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="c">DELETED</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1400948

    expected_core = True
    expected_deleted = True
    result = experiments.do(create_record(snippet))

    assert validate(result['core'], core_schema) is None
    assert expected_core == result['core']

    assert validate(result['deleted'], deleted_schema) is None
    assert expected_deleted == result['deleted']
