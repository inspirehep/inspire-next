# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

"""MARC 21 model definition."""

from __future__ import absolute_import, division, print_function

import six

from dojson import utils
from dojson.errors import IgnoreKey

from ..model import experiments
from ...utils import force_single_element, get_record_ref

from inspirehep.utils.helpers import force_force_list


@experiments.over('experiment_names', '^119..')
@utils.for_each_value
def experiment_names(self, key, value):
    """Experiment names."""
    if value.get('u'):
        self.setdefault('affiliation', [])
        raw_affiliations = force_force_list(value.get('u'))
        for raw_affiliation in raw_affiliations:
            self['affiliation'].append(raw_affiliation)

    return {
        'source': value.get('9'),
        'subtitle': value.get('b'),
        'title': value.get('a'),
    }


@experiments.over('titles', '^245[10_][0_]')
@utils.for_each_value
@utils.filter_values
def titles(self, key, value):
    """Titles."""
    return {
        'title': value.get('a'),
    }


@experiments.over('title_variants', '^419..')
@utils.for_each_value
def title_variants(self, key, value):
    """Title variants."""
    return {
        'title': value.get('a')
    }


@experiments.over('contact_details', '^270..')
@utils.for_each_value
def contact_details(self, key, value):
    name = value.get('p')
    email = value.get('m')

    return {
        'name': name if isinstance(name, six.string_types) else None,
        'email': email if isinstance(email, six.string_types) else None,
    }


@experiments.over('description', '^520..')
@utils.for_each_value
def description(self, key, value):
    """Description of experiment."""
    return value.get("a")


@experiments.over('spokepersons', '^702..')
@utils.for_each_value
def spokespersons(self, key, value):
    """Spokepersons of the experiment."""
    def _get_inspire_id(i_values):
        i_value = force_single_element(i_values)
        if i_value:
            return [
                {
                    'type': 'INSPIRE',
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
    """Collaboration of experiment."""
    values = force_force_list(self.get('collaboration'))
    values.extend(self.get('collaboration_alternative_names', []))
    values.extend(el.get('g') for el in force_force_list(value))

    collaborations = sorted(values, key=len)
    if len(collaborations) > 1:
        self['collaboration_alternative_names'] = collaborations[1:]
    if collaborations:
        return collaborations[0]


@experiments.over('related_experiments', '^510')
@utils.for_each_value
def related_experiments(self, key, value):
    """Related experiments."""
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


@experiments.over('_date_started', '^046..')
def date_started(self, key, value):
    """Date started and completed."""
    values = force_force_list(value)

    for val in values:
        if val.get('s'):
            self['date_started'] = val.get('s')
        if val.get('t'):
            self['date_completed'] = val.get('t')

    raise IgnoreKey


@experiments.over('accelerator', '^693')
def accelerator(self, key, value):
    """Field code."""
    return value.get('a')
