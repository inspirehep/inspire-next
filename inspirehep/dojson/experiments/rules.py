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

"""DoJSON rules for experiments."""

from __future__ import absolute_import, division, print_function

import six

from dojson import utils
from dojson.errors import IgnoreKey

from inspirehep.utils.helpers import force_list
from inspire_schemas.api import LiteratureBuilder

from .model import experiments
from ..utils import force_single_element, get_record_ref


@experiments.over('_date_started', '^046..')
def date_started(self, key, value):
    values = force_list(value)
    for val in values:
        if val.get('q'):
            self['date_proposed'] = val.get('q')
        if val.get('r'):
            self['date_approved'] = val.get('r')
        if val.get('s'):
            self['date_started'] = val.get('s')
        if val.get('t'):
            self['date_completed'] = val.get('t')
        if val.get('c'):
            self['date_cancelled'] = value.get('c')

    raise IgnoreKey


@experiments.over('experiment', '^119..')
def experiment_names(self, key, value):
        exp_value = value.get('c')
        accelerator = self.get('accelerator', {})
        experiment = self.get('experiment', {})

        if value.get('b'):
            accelerator['value'] = value.get('b')
            prj_type = self.get('project_type', [])
            prj_type.append('accelerator')
            self['project_type'] = prj_type
            self['accelerator'] = accelerator

        if value.get('u'):
            institution = self.get('institution', {})
            institution['value'] = value.get('u')
            self['institution'] = institution

        if value.get('a'):
            experiment['legacy_name'] = value.get('a')
            prj_type = self.get('project_type', [])
            prj_type.append('experiment')
            self['project_type'] = prj_type
            if not value.get('c'):
                name_to_split = value.get('a')
                exp_value = name_to_split.split('-')[-1]
            experiment['value'] = exp_value

        if value.get('d'):
            experiment['short_name'] = value.get('d')
        return experiment


@experiments.over('long_name', '^245..')
def title(self, key, value):
    return value.get('a')


@experiments.over('inspire_classification', '^372..')
@utils.for_each_value
def title(self, key, value):
    experiments_list = {
        'Fixed Target Experiments': '2',
        'Hadron Spectroscopy': '2.2',
        'Non-accelerator': '4.1',
        'Proton decay': '6.1',
        'Proton beams': '7.3',
        'Balloon': '5.4',
        'e+ e-': '1.2',
        'CMB': '8.1',
        'Axion search experiments': '4.2',
        'Lattice': '9.1',
        'Ground array': '5.1',
        'Gravitational waves': '8.4',
        'longer baselines': '3.2.2',
        'Lepton precision experiments': '2.6',
        'long-baseline': '3.1.2',
        'short-baseline': '3.1.1',
        'Magnetic monopoles': '6.3',
        'p p': '1.1.2',
        'Drell-Yan/Dilepton production': '2.4',
        'Deep inelastic scattering': '2.3',
        'Electron and positron beams': '7.1',
        'Neutrino (flavor) experiments': '3',
        'Dark Forces': '4.3',
        'Collider Experiments': '1',
        'High-momentum transfer': '2.1',
        'Astronomy experiments': '8',
        'Cerenkov array': '5.2',
        'Non terrestrial': '3.3',
        'Solar': '3.3.2',
        'Fractionally charged particles': '6.4',
        'Flavor physics': '2.5',
        'Neutrino mass': '3.5',
        'Heavy Flavor Factory': '1.4',
        'Atmospheric': '3.3.1',
        'Supernovae': '8.3',
        'Cosmic': '3.3.3',
        'Satellite': '5.3',
        'Heavy ion': '1.5',
        'Cosmic ray experiments': '5',
        'Other Rare-process/exotic experiments': '6',
        'Survey': '8.2',
        'Theory collaborations': '9',
        'Dark matter search experiments': '4',
        'Hadrons': '1.1',
        'e p': '1.3',
        'p anti-p': '1.1.1',
        'Reactor': '3.2',
        'Accelerator': '3.1',
        'Modified gravity and space-time': '6.2',
        'Muon beams': '7.2',
        'Accelerator Test Facility Experiments': '7',
        'ultra-short-baseline': '3.2.1',
        'Neutrinoless double beta decay': '3.4'
        }

    return experiments_list[value.get('a')]


@experiments.over('name_variants', '^419..')
def titles(self, key, value):
    title_var = self.get('name_variants', [])
    for value in force_list(value.get('a')):
        title_var.append(value)
    return title_var


@experiments.over('related_records', '^510..')
@utils.for_each_value
def related_experiments(self, key, value):
    def _get_record(zero_values):
        zero_value = force_single_element(zero_values)
        try:
            recid = int(zero_value)
            return get_record_ref(recid, 'experiments')
        except (TypeError, ValueError):
            return None

    def _classify_relation_type(w_values):
        w_value = force_single_element(w_values)
        return {'a': 'predecessor' }.get(w_value, '')

    record = _get_record(value.get('0'))
    #relation = _classify_relation_type(value.get('w'))
    #if not relation:
    #    relation = 'successor'
    return {
        'relation_freetext': force_single_element(value.get('i')),
        'record': record,
        'relation': _classify_relation_type(value.get('w')),
        'curated_relation': record is not None,
    }


@experiments.over('description', '^520..')
def description(self, key, value):
    description_incl = self.get('description', '')
    if description_incl and value.get('a'):
        description_incl = description_incl + ', ' + value.get('a')
    else:
        description_incl = value.get('a')
    return description_incl


@experiments.over('collaboration', '^710..')
def collaboration(self, key, value):
    collaboration = self.get('collaboration', {})
    if value.get('g'):
        collaboration['value'] = value.get('g')
        prj_type = self.get('project_type', [])
        prj_type.append('collaboration')
        self['project_type'] = prj_type
    if value.get('q'):
        subgroups = collaboration.get('subgroup_names', [])
        subgroups.append(value.get('q'))
        collaboration['subgroup_names'] = subgroups
    return collaboration
