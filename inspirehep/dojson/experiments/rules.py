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

import re

from dojson import utils
from dojson.errors import IgnoreKey

from inspire_schemas.utils import load_schema
from inspirehep.utils.helpers import force_list, maybe_int

from .model import experiments
from ..utils import force_single_element, get_record_ref


@experiments.over('_dates', '^046..')
def dates(self, key, values):
    for value in force_list(values):
        if value.get('q'):
            self['date_proposed'] = value.get('q')
        if value.get('r'):
            self['date_approved'] = value.get('r')
        if value.get('s'):
            self['date_started'] = value.get('s')
        if value.get('c'):
            self['date_cancelled'] = value.get('c')
        if value.get('t'):
            self['date_completed'] = value.get('t')

    raise IgnoreKey


@experiments.over('experiment', '^119..')
def experiment(self, key, values):
    """Populate the ``experiment`` key.

    Also populates the ``accelerator`` and the ``insitution`` key
    through side effects.
    """
    experiment = self.get('experiment', {})
    accelerator = self.get('accelerator', {})
    institution = self.get('institution', {})

    for value in force_list(values):
        if value.get('a'):
            experiment['legacy_name'] = value.get('a')
        if value.get('c'):
            experiment['value'] = value.get('c')
        if value.get('d'):
            experiment['short_name'] = value.get('d')

        if value.get('b'):
            accelerator['value'] = value.get('b')

        if value.get('u'):
            institution['value'] = value.get('u')
        if value.get('z'):
            record = get_record_ref(maybe_int(value.get('z')), 'institutions')
            if record:
                institution['curated_relation'] = True
                institution['record'] = record

    self['accelerator'] = accelerator
    self['institution'] = institution
    return experiment


@experiments.over('long_name', '^245..')
def long_name(self, key, value):
    return value.get('a')


@experiments.over('inspire_classification', '^372..')
@utils.for_each_value
def inspire_classification(self, key, value):
    schema = load_schema('experiments')
    pattern = schema['properties']['inspire_classification']['items']['pattern']

    if re.match(pattern, value.get('a')):
        return value.get('a')


@experiments.over('name_variants', '^419..')
@utils.for_each_value
def name_variants(self, key, value):
    return value.get('a')


@experiments.over('related_experiments', '^510..')
@utils.for_each_value
def related_experiments(self, key, value):
    def _get_relation(w_values):
        w_value = force_single_element(w_values)
        return {'a': 'predecessor', 'b': 'successor'}.get(w_value, '')

    record = get_record_ref(maybe_int(value.get('0')), 'experiments')

    return {
        'curated_relation': record is not None,
        'record': record,
        'relation': _get_relation(value.get('w')),
        'value': force_single_element(value.get('a')),
    }


@experiments.over('description', '^520..')
def description(self, key, value):
    result = self.get('description', '')

    if result and value.get('a'):
        result += '\n' + value.get('a')
    elif value.get('a'):
        result = value.get('a')

    return result


@experiments.over('collaboration', '^710..')
def collaboration(self, key, value):
    record = get_record_ref(maybe_int(value.get('0')), 'experiments')

    return {
        'curated_relation': record is not None,
        'record': record,
        'value': force_single_element(value.get('g')),
    }


@experiments.over('core', '^980..')
def core(self, key, value):
    if not self.get('core'):
        return value.get('a', '').upper() == 'CORE'

    return self.get('core')
