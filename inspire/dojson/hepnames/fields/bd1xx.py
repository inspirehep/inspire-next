# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

from dojson import utils

from ..model import hepnames, hepnames2marc


@hepnames.over('acquisition_source', '^541[10_].')
@utils.for_each_value
@utils.filter_values
def acquisition_source(self, key, value):
    """Immediate Source of Acquisition Note."""
    return {
        'source': value.get('a'),
        'email': value.get('b'),
        'method': value.get('c'),
        'date': value.get('d'),
        'submission_number': value.get('e')
    }


@hepnames2marc.over('541', 'acquisition_source')
@utils.for_each_value
@utils.filter_values
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
    return {
        'value': value.get('a'),
        'numeration': value.get('b'),
        'title': value.get('c'),
        'status': value.get('g'),
        'preferred_name': value.get('q'),
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
@utils.filter_values
def ids(self, key, value):
    """All identifiers, both internal and external."""
    id_type = value.get('9')
    if id_type not in ('arXiv', 'GoogleScholar'):
        id_type = id_type.upper()
    return {
        'value': value.get('a'),
        'type': id_type,
    }


@hepnames2marc.over('035', '^ids$')
@utils.for_each_value
@utils.filter_values
def ids2marc(self, key, value):
    """All identifiers, both internal and external."""
    return {
        'a': value.get('value'),
        '9':  value.get('type'),
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
def native_name(self, key, value):
    """Name in native form."""
    return value.get('a')


@hepnames2marc.over('880', '^native_name$')
def native_name2marc(self, key, value):
    """Name in native form."""
    return {
        'a': value
    }


@hepnames.over('dates', '^800..')
@utils.for_each_value
@utils.filter_values
def dates(self, key, value):
    """Store birth and death dates."""
    dates = {}

    date_parts = value.get('d').split('-')
    dates['birth'] = date_parts[0]
    try:
        dates['death'] = date_parts[1]
    except IndexError:
        pass
    return dates


@hepnames2marc.over('880', '^dates$')
@utils.for_each_value
@utils.filter_values
def dates2marc(self, key, value):
    """Store birth and death dates."""
    death = ""
    if value.get("death"):
        death = "-" + value.get("death")
    return {
        'd': value.get('birth') + death
    }


@hepnames.over('private_current_emails', '^595..')
@utils.for_each_value
def private_current_emails(self, key, value):
    return value.get('m')


@hepnames2marc.over('595', '^private_current_emails$')
@utils.for_each_value
def private_current_emails2marc(self, key, value):
    return {
        'm': value
    }


@hepnames.over('private_old_emails', '^595..')
@utils.for_each_value
def private_old_emails(self, key, value):
    return value.get('o')


@hepnames2marc.over('595', '^private_old_emails$')
@utils.for_each_value
def private_old_emails2marc(self, key, value):
    return {
        'o': value
    }


@hepnames.over('positions', '^371..')
@utils.for_each_value
@utils.filter_values
def positions(self, key, value):
    """Position information.

    Accepted values for 371__r:
    + senior
    + junior
    + staff
    + visitor
    + postdoc
    + phd
    + masters
    + undergrad

    In dates field you can put months in addition to years. In this case you
    have to follow the convention `mth-year`. For example: `10-2012`.
    """
    return {
        'institution': {'name': value.get('a')} if value.get('a') else None,
        'rank': value.get('r'),
        'start_date': value.get('s'),
        'end_date': value.get('t'),
        'email': value.get('m'),
        'old_email': value.get('o'),
        'status': value.get('z')
    }


@hepnames2marc.over('371', '^positions$')
@utils.for_each_value
@utils.filter_values
def positions2marc(self, key, value):
    """Position information.

    Accepted values for 371__r:
    + senior
    + junior
    + staff
    + visitor
    + postdoc
    + phd
    + masters
    + undergrad

    In dates field you can put months in addition to years. In this case you
    have to follow the convention `mth-year`. For example: `10-2012`.
    """
    return {
        'a': value.get('institution', {}).get('name'),
        'r': value.get('rank'),
        's': value.get('start_date'),
        't': value.get('end_date'),
        'm': value.get('email'),
        'o': value.get('old_email'),
        'z': value.get('status')
    }


@hepnames.over('field_categories', '^65017')
@utils.for_each_value
@utils.filter_values
def field_categories(self, key, value):
    return {
        'name': value.get('a').lower(),
        'type': value.get('2'),
    }


@hepnames2marc.over('65017', '^field_categories$')
@utils.for_each_value
@utils.filter_values
def field_categories2marc(self, key, value):
    return {
        'a': value.get('name'),
        '2': value.get('type'),
    }


@hepnames.over('source', '^670..')
@utils.for_each_value
@utils.filter_values
def source(self, key, value):
    return {
        'name': value.get('a'),
        'date_verified': value.get('d'),
    }


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


@hepnames.over('_private_note', '^595..')
@utils.for_each_value
def _private_note(self, key, value):
    return value.get('a')


@hepnames2marc.over('595', '^_private_note$')
@utils.for_each_value
def _private_note2marc(self, key, value):
    return {
        'a': value
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
    except TypeError:
        start_year = None
    try:
        end_year = int(value.get('d'))
    except TypeError:
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
    return {
        'id': value.get("i"),
        'name': value.get("a"),
        'degree_type': degree_type_map.get(value.get("g", "").lower(),
                                           value.get("g"))
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
