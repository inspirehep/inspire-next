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

"""DoJSON rules for MARC fields in 5xx."""

from __future__ import absolute_import, division, print_function

import logging

from dojson import utils

from inspirehep.utils.helpers import force_force_list

from ..model import hep, hep2marc
from ...utils import force_single_element, get_record_ref


logger = logging.getLogger(__name__)


@hep.over('_private_notes', '^595..')
def private_notes(self, key, value):
    def _private_notes(value):
        def _private_note(value, a=None):
            source = value.get('9')
            if value.get('c'):
                source = "CDS"
            return {
                'value': a if a else value.get('b'),
                'source': source,
            }

        if value.get('a'):
            return [_private_note(value, a) for a in force_force_list(value['a'])]
        else:
            return [_private_note(value)]

    private_notes = self.get('_private_notes', [])
    private_notes.extend(_private_notes(value))

    return private_notes


@hep2marc.over('595', '_private_notes')
@utils.for_each_value
def private_notes2marc(self, key, value):
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('thesis_info', '^502..')
def thesis(self, key, value):
    DEGREE_TYPES_MAP = {
        'RAPPORT DE STAGE': 'other',
        'INTERNSHIP REPORT': 'other',
        'DIPLOMA': 'diploma',
        'BACHELOR': 'bachelor',
        'LAUREA': 'laurea',
        'MASTER': 'master',
        'THESIS': 'other',
        'PHD': 'phd',
        'PDF': 'phd',
        'PH.D. THESIS': 'phd',
        'HABILITATION': 'habilitation',
    }

    _degree_type = force_single_element(value.get('b'))
    if _degree_type:
        degree_type = DEGREE_TYPES_MAP.get(_degree_type.upper(), 'other')
    else:
        degree_type = None

    res = {
        'defense_date': value.get('a'),
        'degree_type': degree_type,
        'date': value.get('d'),
    }

    inst_names = force_force_list(value.get('c', []))
    inst_recids = force_force_list(value.get('z', []))
    if len(inst_names) != len(inst_recids):
        institutions = [{'name': name} for name in inst_names]
    else:
        institutions = [{'name': name,
                         'record': get_record_ref(recid, 'institutions'),
                         'curated_relation': True}
                        for name, recid in zip(inst_names, inst_recids)]
    if institutions:
        res['institutions'] = institutions
    return res


@hep2marc.over('502', '^thesis_info$')
def thesis2marc(self, key, value):
    return {
        'a': value.get('defense_date'),
        'b': value.get('degree_type'),
        'c': [inst['name'] for inst in value.get('institutions', [])],
        'd': value.get('date'),
    }


@hep.over('abstracts', '^520..')
@utils.flatten
@utils.for_each_value
def abstracts(self, key, value):
    result = []

    source = force_single_element(value.get('9'))

    for a_value in force_force_list(value.get('a')):
        result.append({
            'source': source,
            'value': a_value,
        })

    for h_value in force_force_list(value.get('h')):
        result.append({
            'source': source,
            'value': h_value,
        })

    return result


@hep2marc.over('520', 'abstracts')
@utils.for_each_value
def abstract2marc(self, key, value):
    source = value.get('source')

    if source == 'HEPDATA':
        return {
            '9': source,
            'h': value.get('value'),
        }

    return {
        '9': source,
        'a': value.get('value'),
    }


@hep.over('funding_info', '^536..')
@utils.for_each_value
def funding_info(self, key, value):
    return {
        'agency': value.get('a'),
        'grant_number': value.get('c'),
        'project_number': value.get('f'),
    }


@hep2marc.over('536', 'funding_info')
@utils.for_each_value
def funding_info2marc(self, key, value):
    return {
        'a': value.get('agency'),
        'c': value.get('grant_number'),
        'f': value.get('project_number'),
    }


@hep.over('license', '^540..')
@utils.for_each_value
def license(self, key, value):
    license_value = force_force_list(value.get('a'))
    # We strip away redundant 'Open Access' string
    license_value = [val for val in license_value if license_value != 'Open Access']
    license_value = force_single_element(license_value)
    return {
        'license': license_value,
        'imposing': value.get('b'),
        'url': value.get('u'),
        'material': value.get('3')
    }


@hep2marc.over('540', '^license$')
@utils.for_each_value
def license2marc(self, key, value):
    return {
        'a': value.get('license'),
        'b': value.get('imposing'),
        'u': value.get('url'),
        '3': value.get('material'),
    }


@hep.over('copyright', '^542[10_].')
@utils.for_each_value
def copyright(self, key, value):
    return {
        'material': value.get('3'),
        'holder': value.get('d'),
        'statement': value.get('f'),
        'url': value.get('u'),
    }


@hep2marc.over('542', 'copyright')
@utils.for_each_value
def copyright2marc(self, key, value):
    return {
        '3': value.get('material'),
        'd': value.get('holder'),
        'f': value.get('statement'),
        'u': value.get('url'),
    }
