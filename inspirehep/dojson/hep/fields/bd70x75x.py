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

from dojson import utils
import re

from inspirehep.utils.helpers import force_force_list

from ..model import hep, hep2marc
from ...utils import get_record_ref

ORCID = re.compile('\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx]')


@hep.over('authors', '^701..')
def thesis_supervisors(self, key, value):
    """Thesis supervisors."""
    def _get_thesis_supervisor(a_value, value):
        return {
            'affiliations': _get_affiliations(value),
            'inspire_roles': ['supervisor'],
            'full_name': a_value,
            'ids': _get_ids(value),
        }

    def _get_affiliations(value):
        result = []

        institutions = force_force_list(value.get('u'))
        recids = force_force_list(value.get('z'))

        # XXX: we zip only when they have the same length, otherwise
        #      we might match a value with the wrong recid.
        if len(institutions) == len(recids):
            for value, recid in zip(institutions, recids):
                try:
                    record = get_record_ref(int(recid), 'institutions')
                except (TypeError, ValueError):
                    record = None

                result.append({
                    'record': record,
                    'value': value,
                })
        else:
            for value in institutions:
                result.append({
                    'value': value,
                })

        return result

    def _get_ids(value):
        def _is_jacow(j_value):
            return j_value.upper().startswith('JACOW-')

        def _is_orcid(j_value):
            return j_value.upper().startswith('ORCID:') and len(j_value) > 6

        def _is_naked_orcid(j_value):
            return ORCID.match(j_value)

        def _is_cern(j_value):
            return j_value.startswith('CCID-')

        result = []

        i_values = force_force_list(value.get('i'))
        for i_value in i_values:
            result.append({
                'type': 'INSPIRE ID',
                'value': i_value,
            })

        j_values = force_force_list(value.get('j'))
        for j_value in j_values:
            if _is_jacow(j_value):
                result.append({
                    'type': 'JACOW',
                    'value': 'JACoW-' + j_value[6:],
                })
            elif _is_orcid(j_value):
                result.append({
                    'type': 'ORCID',
                    'value': j_value[6:],
                })
            elif _is_naked_orcid(j_value):
                result.append({
                    'type': 'ORCID',
                    'value': j_value,
                })
            elif _is_cern(j_value):
                result.append({
                    'type': 'CERN',
                    'value': 'CERN-' + j_value[5:],
                })

        return result

    authors = self.get('authors', [])

    a_values = force_force_list(value.get('a'))
    for a_value in a_values:
        authors.append(_get_thesis_supervisor(a_value, value))

    return authors


@hep.over('collaborations', '^710[10_2][_2]')
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
    collaboration = self.get('collaborations', [])

    filtered_value = value
    for element in filtered_value:
        collaboration.append(get_value(element))

    return collaboration


@hep2marc.over('710', 'collaborations')
@utils.for_each_value
def collaborations2marc(self, key, value):
    """Added Entry-Corporate Name."""
    return {
        'g': value.get('value'),
    }
