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


@experiments.over('name_variants', '^419..')
def titles(self, key, value):
    title_var = self.get('name_variants', [])
    for value in force_list(value.get('a')):
        title_var.append(value)
    return title_var


@experiments.over('related_experiments', '^510..')
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
        return {'a': 'predecessor', 'b': 'successor'}.get(w_value, '')

    record = _get_record(value.get('0'))
    relation = _classify_relation_type(value.get('w'))
    if not relation:
        relation = 'successor'
    return {
        'value': force_single_element(value.get('a')),
        'record': record,
        'relation': relation,
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
