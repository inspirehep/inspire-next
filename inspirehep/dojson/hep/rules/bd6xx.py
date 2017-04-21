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

"""DoJSON rules for MARC fields in 6xx."""

from __future__ import absolute_import, division, print_function

from dojson import utils

from inspirehep.utils.helpers import force_list, maybe_int

from ..model import hep, hep2marc
from ...utils import force_single_element, get_record_ref


@hep.over('accelerator_experiments', '^693..')
def accelerator_experiments(self, key, value):
    result = self.get('accelerator_experiments', [])

    for value in force_list(value):
        e_values = force_list(value.get('e'))
        zero_values = force_list(value.get('0'))

        # XXX: we zip only when they have the same length, otherwise
        #      we might match a value with the wrong recid.
        if len(e_values) == len(zero_values):
            for e_value, zero_value in zip(e_values, zero_values):
                result.append({
                    'legacy_name': e_value,
                    'record': get_record_ref(zero_value, 'experiments'),
                })
        else:
            for e_value in e_values:
                result.append({'legacy_name': e_value})

    return result


@hep2marc.over('693', '^accelerator_experiments$')
@utils.for_each_value
def accelerator_experiments2marc(self, key, value):
    return {'e': value.get('legacy_name')}


@hep.over('keywords', '^(084|653|695)..')
def keywords(self, key, values):
    """Populate the ``keywords`` key.

    Also populates the ``energy_ranges`` key through side effects.
    """
    keywords = self.get('keywords', [])
    energy_ranges = self.get('energy_ranges', [])

    for value in force_list(values):
        if value.get('a'):
            schema = value.get('2', '').upper()
            sources = force_list(value.get('9'))
            keyword = value.get('a')

            if 'conference' not in sources:
                keywords.append({
                    'schema': schema,
                    'source': force_single_element(sources),
                    'value': keyword,
                })

        if value.get('e'):
            energy_ranges.append(maybe_int(value.get('e')))

    self['energy_ranges'] = energy_ranges
    return keywords


@hep2marc.over('695', '^energy_ranges$')
def energy_ranges2marc(self, key, values):
    result_695 = self.get('695', [])

    for value in values:
        result_695.append({
            '2': 'INSPIRE',
            'e': value,
        })

    return result_695


@hep2marc.over('695', '^keywords$')
def keywords2marc(self, key, values):
    """Populate the ``695`` MARC field.

    Also populates the ``084`` and ``6531`` MARC fields through side effects.
    """
    result_695 = self.get('695', [])
    result_084 = self.get('084', [])
    result_6531 = self.get('6531', [])

    for value in values:
        schema = value.get('schema')
        source = value.get('source')
        keyword = value.get('value')

        if schema == 'PACS' or schema == 'PDG':
            result_084.append({
                '2': schema,
                '9': source,
                'a': keyword,
            })
        elif schema == 'JACOW':
            result_6531.append({
                '2': 'JACoW',
                '9': source,
                'a': keyword,
            })
        elif schema == 'INSPIRE':
            result_695.append({
                '2': 'INSPIRE',
                '9': source,
                'a': keyword,
            })
        elif source != 'magpie':
            result_6531.append({
                '9': source,
                'a': keyword,
            })

    self['6531'] = result_6531
    self['084'] = result_084
    return result_695
