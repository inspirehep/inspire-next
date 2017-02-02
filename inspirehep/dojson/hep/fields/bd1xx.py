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
import logging
import re

from dojson import utils

from flask import current_app

from inspirehep.utils.record import get_value as utils_get_value
from inspirehep.utils.helpers import force_force_list

from ..model import hep, hep2marc
from ...utils import (
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
)

from inspirehep.utils.helpers import force_force_list


logger = logging.getLogger(__name__)

ORCID = re.compile('\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx]')


@hep.over('authors', '^[17]00[103_].')
def authors(self, key, value):
    """Authors."""
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

            w_values = force_force_list(value.get('w'))
            for w_value in w_values:
                result.append({
                    'type': 'INSPIRE BAI',
                    'value': w_value,
                })

            return result

        def _get_record(value):
            x_value = force_single_element(value.get('x'))
            if x_value and x_value.isdigit():
                return get_record_ref(x_value, 'authors')

        def _raw_affiliations(val):
            result = []

            v_values = force_force_list(val.get('v'))
            for v_value in v_values:
                result.append({'value': v_value})

            return result

        def _get_contributor_role(value):
            values = force_force_list(value)

            contributor_roles = []
            for value in values:
                value = value.lower()
                if value in current_app.config['INSPIRE_LEGACY_ROLES']['editing']:
                    contributor_roles.append(
                        {
                            'schema': 'CRediT',
                            'value': 'Writing - review & editing'
                        }
                    )
                if value in current_app.config['INSPIRE_LEGACY_ROLES']['administration']:
                    contributor_roles.append(
                        {
                            'schema': 'CRediT',
                            'value': 'Project administration'
                        }
                    )
            return contributor_roles

        return {
            'affiliations': _get_affiliations(value),
            'alternative_names': force_force_list(value.get('q')),
            'curated_relation': value.get('y') == '1',
            'emails': force_force_list(value.get('m')),
            'full_name': _get_full_name(value),
            'ids': _get_ids(value),
            'raw_affiliations': _raw_affiliations(value),
            'record': _get_record(value),
            'contributor_roles': _get_contributor_role(value.get('e')),
        }

    authors = self.get('authors', [])

    values = force_force_list(value)
    for value in values:
        if key.startswith('100'):
            authors.insert(0, _get_author(value))
        else:
            authors.append(_get_author(value))

    return authors


@hep2marc.over('100', '^authors$')
def authors2marc(self, key, value):
    """Main Entry-Personal Name."""
    value = force_force_list(value)

    def get_value(value):
        affiliations = [
            aff.get('value') for aff in value.get('affiliations', [])
        ]
        raw_affiliations = [
            raw_aff.get('value') for raw_aff in value.get('raw_affiliations', [])
        ]

        return {
            'a': value.get('full_name'),
            'e': utils_get_value(value, 'contributor_roles.value'),
            'q': value.get('alternative_names'),
            'i': value.get('inspire_id'),
            'j': value.get('orcid'),
            'm': value.get('emails'),
            'u': affiliations,
            'v': raw_affiliations,
            'x': get_recid_from_ref(value.get('record')),
            'y': value.get('curated_relation')
        }

    if len(value) > 1:
        self["700"] = []
    for author in value[1:]:
        self["700"].append(get_value(author))
    return get_value(value[0])


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
