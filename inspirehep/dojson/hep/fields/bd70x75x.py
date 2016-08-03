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

from six.moves import zip_longest

from dojson import utils

from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import get_value

from ..model import hep, hep2marc
from ...utils import get_record_ref


@hep.over('thesis_supervisors', '^701..')
@utils.for_each_value
def thesis_supervisors(self, key, value):
    """Thesis supervisors.

    FIXME: handle the presence of multiple 700__a.
    FIXME: handle identifiers from 701__i and 701__j."""
    def _get_affiliations(value):
        result = []

        institutions = force_force_list(value.get('u'))
        recids = force_force_list(value.get('z'))

        for value, recid in zip_longest(institutions, recids):
            try:
                record = get_record_ref(int(recid), 'institutions')
            except (TypeError, ValueError):
                record = None

            result.append({
                'curated_relation': record is not None,
                'record': record,
                'value': value,
            })

        return result

    return {
        'full_name': value.get('a'),
        'affiliations': _get_affiliations(value),
    }


@hep2marc.over('701', 'thesis_supervisors')
@utils.for_each_value
def thesis_supervisors2marc(self, key, value):
    """Thesis supervisors.

    FIXME: handle recids to 701__z."""
    return {
        'a': value.get('full_name'),
        'u': get_value(value, 'affiliations.value'),
    }


@hep.over('collaboration', '^710[10_2][_2]')
def collaboration(self, key, value):
    """Added Entry-Corporate Name."""
    value = force_force_list(value)

    def get_value(value):
        recid = None
        if '0' in value:
            try:
                recid = int(value.get('0'))
            except:
                pass
        return {
            'value': value.get('g'),
            'record': get_record_ref(recid, 'experiments')
        }
    collaboration = self.get('collaboration', [])

    filtered_value = value
    for element in filtered_value:
        collaboration.append(get_value(element))

    return collaboration


@hep2marc.over('710', 'collaboration')
@utils.for_each_value
@utils.filter_values
def collaboration2marc(self, key, value):
    """Added Entry-Corporate Name."""
    return {
        'g': value,
    }
