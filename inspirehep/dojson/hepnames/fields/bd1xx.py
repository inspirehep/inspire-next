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

from inspirehep.dojson import utils as inspire_dojson_utils

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
    value = utils.force_list(value)
    self.setdefault('breadcrumb_title', value[0].get('a'))
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
@utils.filter_values
def ids(self, key, value):
    """All identifiers, both internal and external."""
    id_type = value.get('9')
    if id_type and id_type not in ('arXiv', 'GoogleScholar'):
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
def private_current_emails(self, key, value):
    """Hidden information."""
    value = utils.force_list(value)
    private_current_emails = [x.get('m') for x in value if x.get('m')]
    self.setdefault(
        'private_old_emails',
        [x.get('o') for x in value if x.get('o')]
    )
    self.setdefault(
        '_private_note',
        [x.get('a') for x in value if x.get('a')]
    )
    return private_current_emails


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
    curated_relation = False
    recid = ''
    status = ''
    recid_status = utils.force_list(value.get('z'))
    if recid_status:
        for val in recid_status:
            if val.lower() == 'current':
                status = val
            elif type(val) is int:
                recid = val
                curated_relation = True

    return {
        'institution': {'name': value.get('a'), 'recid': recid} if
        value.get('a') else None,
        'rank': value.get('r'),
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
def field_categories(self, key, value):
    """Field categories."""
    def get_value(value):
        if isinstance(value, dict):
            name = value.get('a', '')
        else:
            name = value
        return name

    value = utils.force_list(value)
    field_categories = self.get('field_categories', [])
    for element in value:
        if element.get('a'):
            el = utils.force_list(element.get('a'))
            for val in el:
                field_categories.append(get_value(val))
    return field_categories


@hepnames2marc.over('65017', '^field_categories$')
@utils.for_each_value
def field_categories2marc(self, key, value):
    return {
        'a': value,
        '2': 'INSPIRE',
    }


@hepnames.over('source', '^670..')
def source(self, key, value):
    def get_value(value):
        return {
            'name': value.get('a'),
            'date_verified': value.get('d'),
        }
    source = self.get('source', [])

    value = utils.force_list(value)

    for val in value:
        source.append(get_value(val))

    return inspire_dojson_utils.remove_duplicates_from_list_of_dicts(
        source)


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
        degree_type_raw = utils.force_list(value.get('g'))[0]
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


@hepnames.over('urls', '^856.[10_28]')
@utils.for_each_value
@utils.filter_values
def urls(self, key, value):
    """URL to external resource."""
    return {
        'value': value.get('u'),
        'description': value.get('y'),
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
