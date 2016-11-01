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

"""MARC 21 model definition for HepNames records."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils

from ..model import hepnames, hepnames2marc
from ...utils import (
    classify_rank,
    force_single_element,
    get_record_ref,
    get_recid_from_ref
)

from inspirehep.utils.helpers import force_force_list


INSPIRE_BAI = re.compile('(\w+\.)+\d+')
LOOKS_LIKE_CERN = re.compile('^\d+$|^CER[MN]?-|^CNER-|^CVERN-', re.I)
NON_DIGIT = re.compile('[^\d]+')


@hepnames.over('name', '^100..')
def name(self, key, value):
    """Name information.

    Please note that MARC field for an author's name is splitted into two
    fields, `last_name` and `first_name`. The same situation occurs for
    the date fields, in JSON it is splitted into `birth_year` and `death_year`.

    Admissible string values for `100__g`:
    + active
    + departed
    + retired
    + deceased

    The only accepted value in `100__c` field is:
    + Sir

    Values accepted for `100__b:
    + Jr.
    + Sr.
    + roman numbers (like VII)
    """
    value = force_force_list(value)
    self.setdefault('dates', value[0].get('d'))
    return {
        'value': value[0].get('a'),
        'numeration': value[0].get('b'),
        'title': value[0].get('c'),
        'status': value[0].get('g'),
        'preferred_name': value[0].get('q'),
    }


@hepnames2marc.over('100', '^name$')
def name2marc(self, key, value):
    """Name information.

    Please note that MARC field for an author's name is splitted into two
    fields, `last_name` and `first_name`. The same situation occurs for
    the date fields, in JSON it is splitted into `birth_year` and `death_year`.

    Admissible string values for `100__g`:
    + active
    + departed
    + retired
    + deceased

    The only accepted value in `100__c` field is:
    + Sir

    Values accepted for `100__b:
    + Jr.
    + Sr.
    + roman numbers (like VII)
    """
    return {
        'a': value.get('value'),
        'b': value.get('numeration'),
        'c': value.get('title'),
        'g': value.get('status'),
        'q': value.get('preferred_name'),
    }


@hepnames.over('ids', '^035..')
@utils.for_each_value
def ids(self, key, value):
    """All identifiers, both internal and external."""
    def _get_type(value):
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

    def _guess_type_from_value(a_value):
        if a_value is None:
            return

        if INSPIRE_BAI.match(a_value):
            return 'INSPIRE BAI'

    def _try_to_correct_value(type_, a_value):
        if a_value is None:
            return a_value

        if type_ == 'CERN' and LOOKS_LIKE_CERN.match(a_value):
            return 'CERN-' + NON_DIGIT.sub('', a_value)
        elif type_ == 'KAKEN':
            return 'KAKEN-' + a_value
        else:
            return a_value

    a_value = force_single_element(value.get('a'))

    type_ = _get_type(value)
    if type_ is None:
        type_ = _guess_type_from_value(a_value)

    a_value = _try_to_correct_value(type_, a_value)

    if type_ and a_value:
        return {
            'type': type_,
            'value': a_value,
        }


@hepnames2marc.over('035', '^ids$')
@utils.for_each_value
def ids2marc(self, key, value):
    """All identifiers, both internal and external."""
    return {
        'a': value.get('value'),
        '9': value.get('type'),
    }


@hepnames.over('other_names', '^400..')
def other_names(self, key, value):
    """Other variation of names.

    Usually a different form of writing the primary name.
    """
    other_names = self.get('other_names', [])
    other_names.extend(force_force_list(value.get('a')))

    return other_names


@hepnames2marc.over('400', '^other_names$')
@utils.for_each_value
def other_names2marc(self, key, value):
    """Other variation of names.

    Usually a different form of writing the primary name.
    """
    return {
        'a': value
    }


@hepnames.over('native_name', '^880..')
@utils.for_each_value
def native_name(self, key, value):
    """Name in native form."""
    return value.get('a')


@hepnames2marc.over('880', '^native_name$')
def native_name2marc(self, key, value):
    """Name in native form."""
    return {
        'a': value
    }


@hepnames.over('private_current_emails', '^595..')
@utils.for_each_value
def private_current_emails(self, key, value):
    """Hidden information."""
    if 'o' in value:
        self.setdefault('private_old_emails', []).append(value['o'])
    if 'a' in value:
        self.setdefault('_private_note', []).append(value['a'])
    return value.get('m')


@hepnames2marc.over('595', '^(private_current_emails|_private_note|private_old_emails)$')
@utils.for_each_value
def hidden_notes2marc(self, key, value):
    return {
        'a': value if key == '_private_note' else None,
        'm': value if key == 'private_current_emails' else None,
        'o': value if key == 'private_old_emails' else None,
    }

setattr(hidden_notes2marc, '__extend__', True)


@hepnames.over('positions', '^371..')
@utils.for_each_value
def positions(self, key, value):
    """Positions that an author held during their career."""
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
    """Positions that an author held during their career."""
    return {
        'a': value.get('institution', {}).get('name'),
        'r': value.get('_rank'),
        's': value.get('start_date'),
        't': value.get('end_date'),
        'm': value.get('emails'),
        'o': value.get('old_emails'),
        'z': 'Current' if value.get('current') else None,
    }


@hepnames2marc.over('65017', '^field_categories$')
@utils.for_each_value
def field_categories2marc(self, key, value):
    return {
        'a': value.get('term'),
        '2': value.get('source') or "INSPIRE",
    }


@hepnames.over('source', '^670..')
def source(self, key, value):
    def get_value(value):
        return {
            'name': value.get('a'),
            'date_verified': value.get('d'),
        }
    source = self.get('source', [])

    value = force_force_list(value)

    for val in value:
        source.append(get_value(val))

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
    return {
        'a': value
    }


@hepnames.over('_public_note', '^680..')
@utils.for_each_value
def _public_note(self, key, value):
    return value.get('i')


@hepnames2marc.over('680', '^_public_note$')
@utils.for_each_value
def _public_note2marc(self, key, value):
    return {
        'i': value
    }


@hepnames.over('_curators_note', '^667..')
@utils.for_each_value
def _curators_note(self, key, value):
    return value.get('a')


@hepnames2marc.over('667', '^_curators_note$')
@utils.for_each_value
def _curators_note2marc(self, key, value):
    return {
        'a': value
    }


@hepnames.over('experiments', '^693..')
def experiments(self, key, values):
    """Information about experiments.

    FIXME: use the flatten decorator once DoJSON 1.3.0 is released.
    """
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
    """Information about experiments.

    FIXME: use the flatten decorator once DoJSON 1.3.0 is released.
    """
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
    """The advisors for all types of degrees.

    FIXME: handle identifiers in 701__i and 701__w.
    """
    DEGREE_TYPES_MAP = {
        'Bachelor': 'Bachelor',
        'UG': 'Bachelor',
        'MAS': 'Master',
        'master': 'Master',
        'Master': 'Master',
        'PhD': 'PhD',
        'PHD': 'PhD',
    }

    _degree_type = force_single_element(value.get('g'))
    degree_type = DEGREE_TYPES_MAP.get(_degree_type, 'Other')

    recid = force_single_element(value.get('x'))
    record = get_record_ref(recid, 'authors')

    return {
        'name': value.get('a'),
        'degree_type': degree_type,
        '_degree_type': _degree_type,
        'record': record,
        'curated_relation': value.get('y') == '1'
    }


@hepnames2marc.over('701', '^advisors$')
@utils.for_each_value
def advisors2marc(self, key, value):
    """The advisors for all types of degrees."""
    return {
        'a': value.get('name'),
        'g': value.get('_degree_type'),
        'x': get_recid_from_ref(value.get('record')),
        'y': '1' if value.get('curated_relation') else '0',
    }


@hepnames2marc.over('8564', 'url')
@utils.for_each_value
def url2marc(self, key, value):
    """URL to external resource."""
    return {
        'u': value.get('value'),
        'y': value.get('description'),
    }
