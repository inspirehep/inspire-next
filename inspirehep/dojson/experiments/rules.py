# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016, 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON rules for experiments."""

from __future__ import absolute_import, division, print_function

import six

from dojson import utils
from dojson.errors import IgnoreKey

from inspirehep.utils.helpers import force_force_list

from .model import experiments
from ..utils import force_single_element, get_record_ref


@experiments.over('_date_started', '^046..')
def date_started(self, key, value):
    values = force_force_list(value)

    for val in values:
        if val.get('q'):
            self['date_proposed'] = val.get('q')
        if val.get('r'):
            self['date_approved'] = val.get('r')
        if val.get('s'):
            self['date_started'] = val.get('s')
        if val.get('t'):
            self['date_completed'] = val.get('t')

    raise IgnoreKey


@experiments.over('experiment_names', '^119..')
@utils.for_each_value
def experiment_names(self, key, value):
    if value.get('u'):
        self.setdefault('affiliations', [])

        name = value.get('u')
        recid = value.get('z')
        record = get_record_ref(recid, 'institutions')

        self['affiliations'].append({
            'curated_relation': record is not None,
            'name': name,
            'record': record
        })

    return {
        'source': value.get('9'),
        'subtitle': value.get('b'),
        'title': value.get('a'),
    }


@experiments.over('titles', '^(245|419)..')
def titles(self, key, value):
    titles = self.get('titles', [])

    for value in force_force_list(value):
        if key.startswith('245'):
            titles.insert(0, {'title': value.get('a')})
        else:
            titles.append({'title': value.get('a')})

    return titles


@experiments.over('contact_details', '^270..')
@utils.for_each_value
def contact_details(self, key, value):
    name = value.get('p')
    email = value.get('m')

    return {
        'name': name if isinstance(name, six.string_types) else None,
        'email': email if isinstance(email, six.string_types) else None,
    }


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

    return {
        'name': force_single_element(value.get('a')),
        'record': record,
        'relation': _classify_relation_type(value.get('w')),
        'curated_relation': record is not None,
    }


@experiments.over('description', '^520..')
@utils.for_each_value
def description(self, key, value):
    return value.get('a')


@experiments.over('accelerator', '^693..')
def accelerator(self, key, value):
    return value.get('a')


@experiments.over('spokespersons', '^702..')
@utils.for_each_value
def spokespersons(self, key, value):
    def _get_inspire_id(i_values):
        i_value = force_single_element(i_values)
        if i_value:
            return [
                {
                    'schema': 'INSPIRE ID',
                    'value': i_value,
                },
            ]

    def _is_current(z_values):
        z_value = force_single_element(z_values)
        if z_value and isinstance(z_value, six.string_types):
            return z_value.lower() == 'current'

    def _get_record(x_values):
        x_value = force_single_element(x_values)
        if x_value:
            return get_record_ref(x_value, 'authors')

    record = _get_record(value.get('x'))

    return {
        'current': _is_current(value.get('z')),
        'ids': _get_inspire_id(value.get('i')),
        'name': force_single_element(value.get('a')),
        'record': record,
        'curated_relation': record is not None,
    }


@experiments.over('collaboration', '^710..')
def collaboration(self, key, value):
    values = force_force_list(self.get('collaboration'))
    values.extend(self.get('collaboration_alternative_names', []))
    values.extend(el.get('g') for el in force_force_list(value))

    collaborations = sorted(values, key=len)
    if len(collaborations) > 1:
        self['collaboration_alternative_names'] = collaborations[1:]
    if collaborations:
        return collaborations[0]
