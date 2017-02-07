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

"""DoJSON rules for HEPNames."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils

from inspirehep.utils.helpers import force_force_list

from .model import hepnames, hepnames2marc
from ..utils import (
    classify_rank,
    force_single_element,
    get_record_ref,
    get_recid_from_ref
)


INSPIRE_BAI = re.compile('(\w+\.)+\d+')
LOOKS_LIKE_CERN = re.compile('^\d+$|^CER[MN]?-|^CNER-|^CVERN-', re.I)
NON_DIGIT = re.compile('[^\d]+')


@hepnames.over('ids', '^035..')
@utils.for_each_value
def ids(self, key, value):
    def _get_schema(value):
        IDS_MAP = {
            'ARXIV': 'ARXIV',
            'BAI': 'INSPIRE BAI',
            'CERN': 'CERN',
            'DESY': 'DESY',
            'GOOGLESCHOLAR': 'GOOGLESCHOLAR',
            'INSPIRE': 'INSPIRE ID',
            'KAKEN': 'KAKEN',
            'ORCID': 'ORCID',
            'RESEARCHID': 'RESEARCHERID',
            'RESEARCHERID': 'RESEARCHERID',
            'SLAC': 'SLAC',
            'SCOPUS': 'SCOPUS',
            'VIAF': 'VIAF',
            'WIKIPEDIA': 'WIKIPEDIA',
        }

        return IDS_MAP.get(value.get('9', '').upper())

    def _guess_schema_from_value(a_value):
        if a_value is None:
            return

        if INSPIRE_BAI.match(a_value):
            return 'INSPIRE BAI'

    def _try_to_correct_value(schema, a_value):
        if a_value is None:
            return a_value

        if schema == 'CERN' and LOOKS_LIKE_CERN.match(a_value):
            return 'CERN-' + NON_DIGIT.sub('', a_value)
        elif schema == 'KAKEN':
            return 'KAKEN-' + a_value
        else:
            return a_value

    a_value = force_single_element(value.get('a'))

    schema = _get_schema(value)
    if schema is None:
        schema = _guess_schema_from_value(a_value)

    a_value = _try_to_correct_value(schema, a_value)

    if schema and a_value:
        return {
            'schema': schema,
            'value': a_value,
        }


@hepnames2marc.over('035', '^ids$')
@utils.for_each_value
def ids2marc(self, key, value):
    def _get_9_value(value):
        schema = value.get('schema')

        if schema == 'INSPIRE ID':
            return 'INSPIRE'
        elif schema == 'INSPIRE BAI':
            return 'BAI'
        return schema

    return {
        'a': value.get('value'),
        '9': _get_9_value(value),
    }


@hepnames.over('name', '^100..')
def name(self, key, value):
    self['status'] = force_single_element(value.get('g', '')).lower()

    return {
        'numeration': force_single_element(value.get('b', '')),
        'preferred_name': force_single_element(value.get('q', '')),
        'title': force_single_element(value.get('c', '')),
        'value': force_single_element(value.get('a', '')),
    }


@hepnames2marc.over('100', '^name$')
def name2marc(self, key, value):
    return {
        'a': value.get('value'),
        'b': value.get('numeration'),
        'c': value.get('title'),
        'q': value.get('preferred_name'),
    }


@hepnames2marc.over('100', '^status$')
def status2marc(self, key, value):
    return {'g': value}


@hepnames.over('positions', '^371..')
@utils.for_each_value
def positions(self, key, value):
    curated = False
    current = False
    recid = None

    recid_or_status = force_force_list(value.get('z'))
    for el in recid_or_status:
        if el.lower() == 'current':
            current = True
        else:
            curated = el.isdigit()
            if curated:
                recid = int(el)

    institution = {
        'name': value.get('a'),
        'record': get_record_ref(recid, 'institutions'),
        'curated_relation': curated,
    }

    emails = [el for el in force_force_list(value.get('m'))]
    old_emails = [el for el in force_force_list(value.get('o'))]

    _rank = value.get('r')
    rank = classify_rank(_rank)

    return {
        'institution': institution if institution['name'] else None,
        'emails': emails,
        'old_emails': old_emails,
        '_rank': _rank,
        'rank': rank,
        'start_date': value.get('s'),
        'end_date': value.get('t'),
        'current': current,
    }


@hepnames2marc.over('371', '^positions$')
@utils.for_each_value
def positions2marc(self, key, value):
    return {
        'a': value.get('institution', {}).get('name'),
        'r': value.get('_rank'),
        's': value.get('start_date'),
        't': value.get('end_date'),
        'm': value.get('emails'),
        'o': value.get('old_emails'),
        'z': 'Current' if value.get('current') else None,
    }


@hepnames.over('other_names', '^400..')
def other_names(self, key, value):
    other_names = self.get('other_names', [])
    other_names.extend(force_force_list(value.get('a')))

    return other_names


@hepnames2marc.over('400', '^other_names$')
@utils.for_each_value
def other_names2marc(self, key, value):
    return {'a': value}


@hepnames.over('public_notes', '^667..')
@utils.for_each_value
def _public_notes(self, key, value):
    return {
        'source': value.get('9'),
        'value': value.get('a'),
    }


@hepnames2marc.over('667', '^public_notes$')
@utils.for_each_value
def _public_notes2marc(self, key, value):
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hepnames.over('source', '^670..')
def source(self, key, value):
    def _get_source(value):
        return {
            'name': value.get('a'),
            'date_verified': value.get('d'),
        }

    source = self.get('source', [])

    values = force_force_list(value)
    for value in values:
        source.append(_get_source(value))

    return source


@hepnames2marc.over('670', '^source$')
@utils.for_each_value
def source2marc(self, key, value):
    return {
        'a': value.get('name'),
        'd': value.get('date_verified'),
    }


@hepnames.over('prizes', '^678..')
@utils.for_each_value
def prizes(self, key, value):
    return value.get('a')


@hepnames2marc.over('678', '^prizes$')
@utils.for_each_value
def prizes2marc(self, key, value):
    return {'a': value}


@hepnames.over('experiments', '^693..')
def experiments(self, key, values):
    def _int_or_none(maybe_int):
        try:
            return int(maybe_int)
        except (TypeError, ValueError):
            return None

    def _get_json_experiments(marc_dict):
        start_year = _int_or_none(marc_dict.get('s'))
        end_year = _int_or_none(marc_dict.get('d'))

        names = force_force_list(marc_dict.get('e'))
        recids = force_force_list(marc_dict.get('0'))
        name_recs = zip(names, recids or [None] * len(names))

        for name, recid in name_recs:
            record = get_record_ref(recid, 'experiments')
            yield {
                'curated_relation': record is not None,
                'current': (
                    True if marc_dict.get('z', '').lower() == 'current'
                    else False
                ),
                'end_year': end_year,
                'name': name,
                'record': record,
                'start_year': start_year,
            }

    values = force_force_list(values)
    json_experiments = self.get('experiments', [])
    for experiment in values:
        if experiment:
            json_experiments.extend(_get_json_experiments(experiment))

    return json_experiments


@hepnames2marc.over('693', '^experiments$')
def experiments2marc(self, key, values):
    def _get_marc_experiment(json_dict):
        marc = {
            'e': json_dict.get('name'),
            's': json_dict.get('start_year'),
            'd': json_dict.get('end_year'),
        }
        status = 'current' if json_dict.get('current') else None
        if status:
            marc['z'] = status
        recid = get_recid_from_ref(json_dict.get('record', None))
        if recid:
            marc['0'] = recid
        return marc

    marc_experiments = self.get('693', [])
    values = force_force_list(values)
    for experiment in values:
        if experiment:
            marc_experiments.append(_get_marc_experiment(experiment))

    return marc_experiments


@hepnames.over('advisors', '^701..')
@utils.for_each_value
def advisors(self, key, value):
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

    _degree_type = force_single_element(value.get('g'))
    degree_type = DEGREE_TYPES_MAP.get(_degree_type, 'other')

    recid = force_single_element(value.get('x'))
    record = get_record_ref(recid, 'authors')

    return {
        'name': value.get('a'),
        'degree_type': degree_type,
        'record': record,
        'curated_relation': value.get('y') == '1'
    }


@hepnames2marc.over('701', '^advisors$')
@utils.for_each_value
def advisors2marc(self, key, value):
    return {
        'a': value.get('name'),
        'g': value.get('_degree_type'),
        'x': get_recid_from_ref(value.get('record')),
        'y': '1' if value.get('curated_relation') else '0',
    }


@hepnames.over('native_name', '^880..')
@utils.for_each_value
def native_name(self, key, value):
    return value.get('a')


@hepnames2marc.over('880', '^native_name$')
@utils.for_each_value
def native_name2marc(self, key, value):
    return {'a': value}


@hepnames.over('deleted', '^980..')
def deleted(self, key, value):
    """Populate the ``deleted`` key.

    Also populates the ``stub`` key through side effects.
    """
    def _is_deleted(value):
        return force_single_element(value.get('c', '')).upper() == 'DELETED'

    def _is_stub(value):
        return not (force_single_element(value.get('a', '')).upper() == 'USEFUL')

    deleted = self.get('deleted')
    stub = self.get('stub')

    for value in force_force_list(value):
        deleted = not deleted and _is_deleted(value)
        stub = not stub and _is_stub(value)

    self['stub'] = stub
    return deleted


@hepnames2marc.over('980', '^deleted$')
@utils.for_each_value
def deleted2marc(self, key, value):
    if value:
        return {'c': 'DELETED'}


@hepnames2marc.over('980', '^stub$')
@utils.for_each_value
def stub2marc(self, key, value):
    if not value:
        return {'a': 'USEFUL'}
