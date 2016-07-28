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

from dojson import utils

from ..model import hepnames, hepnames2marc
from ...utils import classify_rank, get_record_ref

from inspirehep.utils.helpers import force_force_list


@hepnames.over('acquisition_source', '^541[10_].')
def acquisition_source(self, key, value):
    """Immediate Source of Acquisition Note."""
    return {
        'source': value.get('a'),
        'email': value.get('b'),
        'method': value.get('c'),
        'date': value.get('d'),
        'submission_number': str(value.get('e'))
    }


@hepnames2marc.over('541', 'acquisition_source')
def acquisition_source2marc(self, key, value):
    """Immediate Source of Acquisition Note."""
    return {
        'a': value.get('source'),
        'b': value.get('email'),
        'c': value.get('method'),
        'd': value.get('date'),
        'e': value.get('submission_number'),
    }


@hepnames.over('name', '^100..')
@utils.filter_values
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
@utils.filter_values
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
    return {
        'value': value.get('a'),
        'type': value.get('9'),
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
@utils.for_each_value
def other_names(self, key, value):
    """Other variation of names.

    Usually a different form of writing the primary name.
    """
    return value.get('a')


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
@utils.filter_values
def hidden_notes2marc(self, key, value):
    return {
        'a': value if key == '_private_note' else None,
        'm': value if key == 'private_current_emails' else None,
        'o': value if key == 'private_old_emails' else None,
    }

setattr(hidden_notes2marc, '__extend__', True)


@hepnames.over('positions', '^371..')
@utils.for_each_value
@utils.filter_values
def positions(self, key, value):
    """Position information.

    In dates field you can put months in addition to years. In this case you
    have to follow the convention `mth-year`. For example: `10-2012`.
    """
    curated_relation = False
    recid = None
    status = ''
    recid_status = force_force_list(value.get('z'))
    for val in recid_status:
        if val.lower() == 'current':
            status = val
        else:
            try:
                recid = int(val)
                curated_relation = True
            except ValueError:
                pass

    inst = {
        'name': value.get('a'),
        'record': get_record_ref(recid, 'institutions')
    }

    _rank = value.get('r')
    rank = classify_rank(_rank)

    return {
        'institution': inst if inst['name'] else None,
        '_rank': _rank,
        'rank': rank,
        'start_date': value.get('s'),
        'end_date': value.get('t'),
        'email': value.get('m'),
        'old_email': value.get('o'),
        'status': status,
        'curated_relation': curated_relation,
    }


@hepnames2marc.over('371', '^positions$')
@utils.for_each_value
@utils.filter_values
def positions2marc(self, key, value):
    """Position information.

    In dates field you can put months in addition to years. In this case you
    have to follow the convention `mth-year`. For example: `10-2012`.
    """
    return {
        'a': value.get('institution', {}).get('name'),
        'r': value.get('_rank'),
        's': value.get('start_date'),
        't': value.get('end_date'),
        'm': value.get('email'),
        'o': value.get('old_email'),
        'z': value.get('status')
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
@utils.filter_values
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
@utils.for_each_value
@utils.filter_values
def experiments(self, key, value):
    """Information about experiments.

    Currently the ``id`` subfield stores the name of the experiment. It should
    be moved to storing id of the experiment as soon as experiments are
    available as records.
    """
    try:
        start_year = int(value.get('s'))
    except (TypeError, ValueError):
        start_year = None
    try:
        end_year = int(value.get('d'))
    except (TypeError, ValueError):
        end_year = None

    return {
        'id': value.get('i'),
        'name': value.get('e'),
        'start_year': start_year,
        'end_year': end_year,
        'status': value.get('z')
    }


@hepnames2marc.over('693', '^experiments$')
@utils.for_each_value
@utils.filter_values
def experiments2marc(self, key, value):
    """Information about experiments.

    Currently the ``id`` subfield stores the name of the experiment. It should
    be moved to storing id of the experiment as soon as experiments are
    available as records.
    """
    return {
        'i': value.get('id'),
        'e': value.get('name'),
        's': value.get('start_year'),
        'd': value.get('end_year'),
        'z': value.get('status')
    }


@hepnames.over('phd_advisors', '^701..')
@utils.for_each_value
@utils.filter_values
def phd_advisors(self, key, value):
    degree_type_map = {
        "phd": "PhD",
        "master": "Master"
    }
    degree_type = None
    if value.get("g"):
        degree_type_raw = force_force_list(value.get('g'))[0]
        degree_type = degree_type_map.get(
            degree_type_raw.lower(),
            degree_type_raw
        )
    return {
        'id': value.get("i"),
        'name': value.get("a"),
        'degree_type': degree_type
    }


@hepnames2marc.over('701', '^phd_advisors$')
@utils.for_each_value
@utils.filter_values
def phd_advisors2marc(self, key, value):
    return {
        'i': value.get("id"),
        'a': value.get("name"),
        'g': value.get("degree_type")
    }


@hepnames2marc.over('8564', 'url')
@utils.for_each_value
@utils.filter_values
def url2marc(self, key, value):
    """URL to external resource."""
    return {
        'u': value.get('value'),
        'y': value.get('description'),
    }
