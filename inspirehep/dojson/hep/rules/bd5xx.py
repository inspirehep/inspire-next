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

from dojson import utils

from inspirehep.utils.helpers import force_force_list

from ..model import hep, hep2marc
from ...utils import force_single_element, get_record_ref


@hep.over('thesis_info', '^502..')
def thesis_info(self, key, value):
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
def thesis_info2marc(self, key, value):
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


@hep2marc.over('520', '^abstracts$')
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


@hep2marc.over('536', '^funding_info$')
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
        'material': value.get('3'),
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


@hep.over('copyright', '^542..')
@utils.for_each_value
def copyright(self, key, value):
    return {
        'material': value.get('3'),
        'holder': value.get('d'),
        'statement': value.get('f'),
        'url': value.get('u'),
    }


@hep2marc.over('542', '^copyright$')
@utils.for_each_value
def copyright2marc(self, key, value):
    return {
        '3': value.get('material'),
        'd': value.get('holder'),
        'f': value.get('statement'),
        'u': value.get('url'),
    }


@hep.over('_private_notes', '^595.[^DH]')
def _private_notes(self, key, value):
    """Populate the ``_private_notes`` key.

    Also populates the ``export_to`` key through side effects.
    """
    def _is_for_cds(value):
        return value.get('c', '').upper() == 'CDS'

    def _is_for_hal(value):
        return value.get('c', '').upper() == 'HAL'

    def _is_not_for_hal(value):
        return value.get('c', '').upper() == 'NOT HAL'

    _private_notes = self.get('_private_notes', [])
    _export_to = self.get('_export_to', {})

    for value in force_force_list(value):
        if _is_for_cds(value):
            _export_to['CDS'] = True
        elif _is_for_hal(value):
            _export_to['HAL'] = True
        elif _is_not_for_hal(value):
            _export_to['HAL'] = False

        source = force_single_element(value.get('9'))
        for _private_note in force_force_list(value.get('a')):
            _private_notes.append({
                'source': source,
                'value': _private_note,
            })

    self['_export_to'] = _export_to
    return _private_notes


@hep2marc.over('595', '^_private_notes$')
def _private_notes2marc(self, key, value):
    """Populate the ``595`` MARC key.

    Also populates the `595_H` MARC key through side effects.
    """
    def _is_from_hal(value):
        return value.get('source') == 'HAL'

    result_595 = self.get('595', [])
    result_595_H = self.get('595_H', [])

    for value in force_force_list(value):
        if _is_from_hal(value):
            result_595_H.append({
                'a': value.get('value'),
            })
        else:
            result_595.append({
                '9': value.get('source'),
                'a': value.get('value'),
            })

    self['595_H'] = result_595_H
    return result_595


@hep2marc.over('595', '^_export_to$')
def _export_to2marc(self, key, value):
    def _is_for_cds(value):
        return 'CDS' in value

    def _is_for_hal(value):
        return 'HAL' in value and value['HAL']

    def _is_not_for_hal(value):
        return 'HAL' in value and not value['HAL']

    result = []

    if _is_for_cds(value):
        result.append({'c': 'CDS'})
    elif _is_for_hal(value):
        result.append({'c': 'HAL'})
    elif _is_not_for_hal(value):
        result.append({'c': 'not HAL'})

    return result


@hep.over('_desy_bookkeeping', '^595.D')
@utils.for_each_value
def _desy_bookkeeping(self, key, value):
    return {
        'date': value.get('d'),
        'expert': value.get('a'),
        'status': value.get('s'),
    }


@hep2marc.over('595_D', '^_desy_bookkeeping$')
@utils.for_each_value
def _desy_bookkeeping2marc(self, key, value):
    return {
        'a': value.get('expert'),
        'd': value.get('date'),
        's': value.get('status'),
    }


@hep.over('_private_notes', '^595.H')
def _private_notes_hal(self, key, value):
    _private_notes = self.get('_private_notes', [])

    for value in force_force_list(value):
        for _private_note in force_force_list(value.get('a')):
            _private_notes.append({
                'source': 'HAL',
                'value': _private_note,
            })

    return _private_notes
