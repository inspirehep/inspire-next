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
import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.experiments import experiments
from inspirehep.dojson.utils import validate


def test_experiment_dates_from_marcxml_046():
    schema = load_schema('experiments')
    subschema_q = schema['properties']['date_proposed']
    subschema_r = schema['properties']['date_approved']
    subschema_s = schema['properties']['date_started']
    subschema_t = schema['properties']['date_completed']
    subschema_c = schema['properties']['date_cancelled']

    snippet = (
        '<record>'
        '  <datafield tag="046" ind1=" " ind2=" ">'
        '    <subfield code="q">2014</subfield>'
        '    <subfield code="r">2015</subfield>'
        '    <subfield code="s">1995</subfield>'
        '    <subfield code="t">2008</subfield>'
        '    <subfield code="c">2016</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected_q = '2014'
    expected_r = '2015'
    expected_s = '1995'
    expected_t = '2008'
    expected_c = '2016'

    result = experiments.do(create_record(snippet))

    assert validate(result['date_proposed'], subschema_q) is None
    assert expected_q == result['date_proposed']

    assert validate(result['date_approved'], subschema_r) is None
    assert expected_r == result['date_approved']

    assert validate(result['date_started'], subschema_s) is None
    assert expected_s == result['date_started']

    assert validate(result['date_completed'], subschema_t) is None
    assert expected_t == result['date_completed']

    assert validate(result['date_cancelled'], subschema_c) is None
    assert expected_c == result['date_cancelled']


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


def test_experiment_names_from_marcxml_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '    <subfield code="c">NA61</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = {
            'legacy_name': 'CERN-ALPHA',
            'value': 'NA61',
        }

    result = experiments.do(create_record(snippet))

    assert validate(result['experiment'], subschema) is None
    assert expected == result['experiment']


def test_experiment_names_from_marcxml_119__c():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = {
            'legacy_name': 'CERN-ALPHA',
            'value': 'ALPHA',
        }

    result = experiments.do(create_record(snippet))

    assert validate(result['experiment'], subschema) is None
    assert expected == result['experiment']


def test_experiment_names_for_project_type_from_marcxml_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['project_type']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '    <subfield code="c">NA61</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = ['experiment']

    result = experiments.do(create_record(snippet))

    assert validate(result['project_type'], subschema) is None
    assert expected == result['project_type']


def test_experiment_names_and_affiliations_from_marcxml_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment']
    subschema_acc = schema['properties']['accelerator']
    subschema_inst = schema['properties']['institution']

    snippet = (
        '<record>'
        '  <datafield tag="119" ind1=" " ind2=" ">'
        '    <subfield code="a">CERN-ALPHA</subfield>'
        '    <subfield code="u">CERN</subfield>'
        '    <subfield code="c">NA61</subfield>'
        '    <subfield code="b">LHC</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1108206

    result = experiments.do(create_record(snippet))

    assert validate(result['experiment'], subschema) is None
    assert result['experiment'] == {
            'legacy_name': 'CERN-ALPHA',
            'value': 'NA61',
        }

    assert validate(result['accelerator'], subschema_acc) is None
    assert result['accelerator'] == {
            'value': 'LHC'
        }

    assert validate(result['institution'], subschema_inst) is None
    assert result['institution'] == {
            'value': 'CERN'
        }


def test_experiment_names_from_marcxml_multiple_119():
    schema = load_schema('experiments')
    subschema = schema['properties']['experiment']
    subschema_inst = schema['properties']['institution']

    snippet = (
        '<record>'
        '   <datafield tag="119" ind1=" " ind2=" ">'
        '       <subfield code="a">DEAP-3600</subfield>'
        '   </datafield>'
        '   <datafield tag="119" ind1=" " ind2=" ">'
        '       <subfield code="u">Non-Accelerator Experiments</subfield>'
        '   </datafield>'
        '</record>'
    )  # record 1108195

    expected = {
            'legacy_name': 'DEAP-3600',
            'value': '3600'
        }
    institution_exp = {
            'value': 'Non-Accelerator Experiments'
            }
    result = experiments.do(create_record(snippet))

    assert validate(result['experiment'], subschema) is None
    assert expected == result['experiment']

    assert validate(result['institution'], subschema_inst) is None
    assert institution_exp == result['institution']


def test_titles_from_marcxml_245__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['long_name']

    snippet = (
        '<record>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        '    <subfield code="a">The ALPHA experiment</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = 'The ALPHA experiment'

    result = experiments.do(create_record(snippet))

    assert validate(result['long_name'], subschema) is None
    assert expected == result['long_name']

def test_titles_from_marcxml_372__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['inspire_classification']

    snippet = (
        '<record>'
        '  <datafield tag="372" ind1=" " ind2=" ">'
        '    <subfield code="a">Electron and positron beams</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = ['7.1']

    result = experiments.do(create_record(snippet))

    assert validate(result['inspire_classification'], subschema) is None
    assert expected == result['inspire_classification']


def test_titles_from_419__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['name_variants']

    snippet = (
        '<datafield tag="419" ind1=" " ind2=" ">'
        '  <subfield code="a">ALPHA</subfield>'
        '  <subfield code="a">Alphas</subfield>'
        '  <subfield code="a">Al</subfield>'
        '</datafield>'
    )  # record/1108206

    expected = ['ALPHA', 'Alphas', 'Al']
    result = experiments.do(create_record(snippet))
    print (result)
    assert validate(result['name_variants'], subschema) is None
    assert expected == result['name_variants']


def test_titles_from_multiple_419__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['name_variants']

    snippet = (
        '<record>'
        '   <datafield tag="419" ind1=" " ind2=" ">'
        '       <subfield code="a">DEAPCLEAN</subfield>'
        '   </datafield>'
        '   <datafield tag="419" ind1=" " ind2=" ">'
        '       <subfield code="a">DEAP-CLEAN</subfield>'
        '   </datafield>'
        '</record>'
    )  # record/1108195

    expected = ['DEAPCLEAN', 'DEAP-CLEAN']
    result = experiments.do(create_record(snippet))
    print (result)
    assert validate(result['name_variants'], subschema) is None
    assert expected == result['name_variants']


def test_description_from_520__a():
    schema = load_schema('experiments')
    subschema = schema['properties']['description']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">The Muon Accelerator Program (MAP) was created in 2010 to unify the DOE supported R&amp;D in the U.S. aimed at developing the concepts and technologies required for Muon Colliders and Neutrino Factories. These muon based facilities have the potential to discover and explore new exciting fundamental physics, but will require the development of demanding technologies and innovative concepts. The MAP aspires to prove the feasibility of a Muon Collider within a few years, and to make significant contributions to the international effort devoted to developing Neutrino Factories. MAP was formally approved on March 18, 2011.</subfield>'
        '</datafield>'
    )  # record/1108188

    expected = 'The Muon Accelerator Program (MAP) was created in 2010 to unify the DOE supported R&D in the U.S. aimed at developing the concepts and technologies required for Muon Colliders and Neutrino Factories. These muon based facilities have the potential to discover and explore new exciting fundamental physics, but will require the development of demanding technologies and innovative concepts. The MAP aspires to prove the feasibility of a Muon Collider within a few years, and to make significant contributions to the international effort devoted to developing Neutrino Factories. MAP was formally approved on March 18, 2011.'
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

    expected = 'DAMA is an observatory for rare processes which develops and uses several low-background set-ups at the Gran Sasso National Laboratory of the I.N.F.N. (LNGS). The main experimental set-ups are: i) DAMA/NaI (about 100 kg of highly radiopure NaI(Tl)), which completed its data taking on July 2002, ii) DAMA/LXe (about 6.5 kg liquid Kr-free Xenon enriched either in 129Xe or in 136Xe), iii) DAMA/R&D, devoted to tests on prototypes and to small scale experiments, mainly on the investigations of double beta decay modes in various isotopes. iv) the second generation DAMA/LIBRA set-up (about 250 kg highly radiopure NaI(Tl)) in operation since March 2003, v) the low background DAMA/Ge detector mainly devoted to sample measurements: in some measurements on rare processes the low-background Germanium detectors of the LNGS facility are also used. Moreover, a third generation R&D is in progress towards a possible 1 ton set-up, DAMA proposed in 1996. In particular, the DAMA/NaI and the DAMA/LIBRA set-ups have investigated the presence of Dark Matter particles in the galactic halo by exploiting the Dark Matter annual modulation signature.'

    result = experiments.do(create_record(snippet))
    assert validate(result['description'], subschema) is None
    assert expected == result['description']


def test_collaboration_from_710():
    schema = load_schema('experiments')
    subschema = schema['properties']['collaboration']

    snippet = (
        '<datafield tag="710" ind1=" " ind2=" ">'
        '  <subfield code="g">DarkSide</subfield>'
        '  <subfield code="q">ATLAS TDAQ</subfield>'
        '</datafield>'
    )  # record/1108199

    expected = {
        'subgroup_names': ['ATLAS TDAQ'],
        'value': 'DarkSide',
    }
    result = experiments.do(create_record(snippet))
    print(result)

    assert validate(result['collaboration'], subschema) is None
    assert result['collaboration'] == expected


def test_related_experiments_from_510_i_w_0():
    schema = load_schema('experiments')
    subschema = schema['properties']['related_records']

    snippet = (
        '<datafield tag="510" ind1=" " ind2=" ">'
        '  <subfield code="0">1262631</subfield>'
        '  <subfield code="w">b</subfield>'
        '  <subfield code="i">b</subfield>'
        '</datafield>'
    )  # record/1108192

    expected = [{'record': {'$ref': 'http://localhost:5000/api/experiments/1262631'},
                'relation_freetext': 'b', 'curated_relation': True}]
    result = experiments.do(create_record(snippet))
    print (result)
    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']


def test_related_experiments_from_double_510__a_w_0():
    schema = load_schema('experiments')
    subschema = schema['properties']['related_records']

    snippet = (
        '<record>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">1108293</subfield>'
        '    <subfield code="w">a</subfield>'
        '  </datafield>'
        '  <datafield tag="510" ind1=" " ind2=" ">'
        '    <subfield code="0">1386527</subfield>'
        '    <subfield code="w">a</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1386519

    expected = [
        {
            'record': {'$ref': 'http://localhost:5000/api/experiments/1108293'},
            'relation': 'predecessor',
            'curated_relation': True,
        },
        {
            'record': {'$ref': 'http://localhost:5000/api/experiments/1386527'},
            'relation': 'predecessor',
            'curated_relation': True,
        },
    ]
    result = experiments.do(create_record(snippet))

    assert validate(result['related_records'], subschema) is None
    assert expected == result['related_records']
