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

"""DoJSON rules for MARC fields in 1xx."""

from __future__ import absolute_import, division, print_function

import logging
import re

from dojson import utils

from inspirehep.utils.helpers import force_force_list

from ..model import hep, hep2marc
from ...utils import (
    force_single_element,
    get_record_ref,
)


logger = logging.getLogger(__name__)

ORCID = re.compile('\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx]')


@hep.over('authors', '^[17]0[01]..')
def authors(self, key, value):
    def _get_author(value):
        def _get_affiliations(value):
            result = []

            u_values = force_force_list(value.get('u'))
            z_values = force_force_list(value.get('z'))

            # XXX: we zip only when they have the same length, otherwise
            #      we might match a value with the wrong recid.
            if len(u_values) == len(z_values):
                for u_value, z_value in zip(u_values, z_values):
                    result.append({
                        'record': get_record_ref(z_value, 'institutions'),
                        'value': u_value,
                    })
            else:
                for u_value in u_values:
                    result.append({'value': u_value})

            return result

        def _get_curated_relation(value):
            if value.get('y') == '1':
                return True
            return  # XXX: we don't return False because it would be preserved.

        def _get_full_name(value):
            a_values = force_force_list(value.get('a'))
            if a_values:
                if len(a_values) > 1:
                    logger.warning(
                        'Record with mashed up authors list. '
                        'Taking first author: %s', a_values[0]
                    )

                return a_values[0]

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
                    'schema': 'INSPIRE ID',
                    'value': i_value,
                })

            j_values = force_force_list(value.get('j'))
            for j_value in j_values:
                if _is_jacow(j_value):
                    result.append({
                        'schema': 'JACOW',
                        'value': 'JACoW-' + j_value[6:],
                    })
                elif _is_orcid(j_value):
                    result.append({
                        'schema': 'ORCID',
                        'value': j_value[6:],
                    })
                elif _is_naked_orcid(j_value):
                    result.append({
                        'schema': 'ORCID',
                        'value': j_value,
                    })
                elif _is_cern(j_value):
                    result.append({
                        'schema': 'CERN',
                        'value': 'CERN-' + j_value[5:],
                    })

            w_values = force_force_list(value.get('w'))
            for w_value in w_values:
                result.append({
                    'schema': 'INSPIRE BAI',
                    'value': w_value,
                })

            return result

        def _get_inspire_roles(value):
            result = []

            if value.get('e', '').lower().startswith('ed'):
                result.append('editor')

            if key.startswith('701'):
                result.append('supervisor')

            return result

        def _get_raw_affiliations(value):
            result = []

            values = force_force_list(value.get('v'))
            for value in values:
                result.append({
                    'value': value,
                })

            return result

        def _get_record(value):
            x_value = force_single_element(value.get('x'))
            if x_value and x_value.isdigit():
                return get_record_ref(x_value, 'authors')

        return {
            'affiliations': _get_affiliations(value),
            'alternative_names': force_force_list(value.get('q')),
            'curated_relation': _get_curated_relation(value),
            'emails': force_force_list(value.get('m')),
            'full_name': _get_full_name(value),
            'ids': _get_ids(value),
            'record': _get_record(value),
            'inspire_roles': _get_inspire_roles(value),
            'raw_affiliations': _get_raw_affiliations(value),
        }

    authors = self.get('authors', [])

    values = force_force_list(value)
    for value in values:
        authors.append(_get_author(value))

    return authors


@hep2marc.over('100', '^authors$')
def authors2marc(self, key, value):
    value = force_force_list(value)

    def _get_ids(value):
        ids = {
            'i': [],
            'j': [],
        }
        if value.get('ids'):
            for _id in value.get('ids'):
                if _id.get('schema') == 'INSPIRE ID':
                    ids['i'].append(_id.get('value'))
                elif _id.get('schema') == 'ORCID':
                    ids['j'].append('ORCID:' + _id.get('value'))
                elif _id.get('schema') == 'JACOW':
                    ids['j'].append(_id.get('value'))
                elif _id.get('schema') == 'CERN':
                    ids['j'].append('CCID-' + _id.get('value')[5:])
        return ids

    def _get_affiliations(value):
        return [
            aff.get('value') for aff in value.get('affiliations', [])
        ]

    def _get_inspire_roles(value):
        values = force_force_list(value.get('inspire_roles'))
        return ['ed.' for role in values if role == 'editor']

    def _get_raw_affiliations(value):
        return [
            aff.get('value') for aff in value.get('raw_affiliations', [])
        ]

    def get_value_100_700(value):
        ids = _get_ids(value)
        return {
            'a': value.get('full_name'),
            'e': _get_inspire_roles(value),
            'q': value.get('alternative_names'),
            'i': ids.get('i'),
            'j': ids.get('j'),
            'm': value.get('emails'),
            'u': _get_affiliations(value),
            'v': _get_raw_affiliations(value),
        }

    def get_value_701(value):
        ids = _get_ids(value)
        return {
            'a': value.get('full_name'),
            'q': value.get('alternative_names'),
            'i': ids.get('i'),
            'j': ids.get('j'),
            'u': _get_affiliations(value),
            'v': _get_raw_affiliations(value),
        }

    if len(value) > 1:
        self["700"] = []
        self["701"] = []

    for author in value[1:]:
        is_supervisor = 'supervisor' in author.get('inspire_roles', [])
        if is_supervisor:
            self["701"].append(get_value_701(author))
        else:
            self["700"].append(get_value_100_700(author))
    return get_value_100_700(value[0])


@hep.over('corporate_author', '^110[10_2].')
@utils.for_each_value
def corporate_author(self, key, value):
    """Main Entry-Corporate Name."""
    return value.get('a')


@hep2marc.over('110', '^corporate_author$')
@utils.for_each_value
def corporate_author2marc(self, key, value):
    """Main Entry-Corporate Name."""
    return {
        'a': value,
    }
