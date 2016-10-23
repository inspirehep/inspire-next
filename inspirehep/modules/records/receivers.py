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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Record receivers."""

from __future__ import absolute_import, division, print_function

import six
from flask import current_app

from invenio_indexer.signals import before_record_index
from invenio_records.signals import before_record_insert, before_record_update

from inspirehep.dojson.utils import classify_field, get_recid_from_ref
from inspirehep.modules.pidstore.providers import InspireRecordIdProvider
from inspirehep.utils.date import create_valid_date
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record import (
    get_value,
    merge_pidstores_of_two_merged_records,
    soft_delete_pidstore_for_record,
)
from inspirehep.utils.record_getter import get_db_record

from .experiments import EXPERIMENTS_MAP
from .signals import after_record_enhanced


@before_record_index.connect
def enhance_record(sender, json, *args, **kwargs):
    """Runs all the record enhancers and fires the after_record_enhanced signals
       to allow receivers work with a fully populated record."""
    populate_inspire_subjects(sender, json, *args, **kwargs)
    populate_inspire_document_type(sender, json, *args, **kwargs)
    match_valid_experiments(sender, json, *args, **kwargs)
    dates_validator(sender, json, *args, **kwargs)
    add_recids_and_validate(sender, json, *args, **kwargs)
    after_record_enhanced.send(json)


@before_record_insert.connect
@before_record_update.connect
def normalize_field_categories(sender, *args, **kwargs):
    """Normalize the content of the `field_categories` key.

    We use the heuristic that a field is normalized if its scheme is 'INSPIRE'
    or if it contains either the `_scheme` key or the `_term` key.

    If the field wasn't normalized we use some mapping defined in the
    configuration to output a `term` belonging to a known set of values.

    We also use the heuristic that the source is 'INSPIRE' if it contains the
    word 'automatically', otherwise we preserve it.

    Note that the valid `scheme`s are hardcoded in the schema, so any
    non-recognized scheme will fail schema validation.
    """
    def _is_normalized(field):
        return (
            field.get('scheme') == 'INSPIRE'
            or '_scheme' in field
            or '_term' in field
        )

    for i, field in enumerate(sender.get('field_categories', [])):
        if _is_normalized(field):
            continue

        original_term = field.get('term')
        normalized_term = classify_field(original_term)
        scheme = 'INSPIRE' if normalized_term else None

        original_scheme = field.get('scheme')
        if isinstance(original_scheme, (list, tuple)):
            original_scheme = original_scheme[0]

        updated_field = {
            '_scheme': original_scheme,
            'scheme': scheme,
            '_term': original_term,
            'term': normalized_term,
        }

        source = field.get('source')
        if source:
            if 'automatically' in source:
                source = 'INSPIRE'
            updated_field['source'] = source

        sender['field_categories'][i].update(updated_field)


def populate_inspire_subjects(sender, json, *args, **kwargs):
    """Populate the INSPIRE subjects before indexing.

    Adds the `facet_inspire_subjects` key to the record, to be used for
    faceting in the search interface. Valid terms on which to facet are
    only those that come from the INSPIRE scheme.
    """
    def _scheme_is_inspire(field):
        return field.get('scheme') == 'INSPIRE'

    inspire_subjects = [
        field['term'] for field in json.get('field_categories', [])
        if _scheme_is_inspire(field) and field.get('term')]

    json['facet_inspire_subjects'] = inspire_subjects


def populate_inspire_document_type(sender, json, *args, **kwargs):
    """Populate the INSPIRE doc type before indexing.

    Adds the `facet_inspire_doc_type` key to the record, to be used for
    faceting in the search interface. Valid document types on which to
    facet are derived from the following algorithm:

    - If the record has no `collections` key, return `[]`.
    - Otherwise:
      - If the record has as a primary collection a key in the following
        table then add the corresponding value to the document types.
        Only the first value found is added.

          + --------------- + ---------------- +
          | key             | value            |
          + --------------- + ---------------- +
          | published       | peer reviewed    |
          | thesis          | thesis           |
          | book            | book             |
          | bookchapter     | bookchapter      |
          | proceedings     | proceedings      |
          | conferencepaper | conference paper |
          | note            | note             |
          | report          | report           |
          | activityreport  | activity report  |
          + --------------- + ---------------- +

      - Otherwise:
        - If the record has no `start_page` and `artid` key in any of
          its `publication_info`s then add 'preprint' to the document types.
      - If the record has as a primary collection a key in the following
        table then add the corresponding value to the document types.
        All values found are added.

          + -------- + -------- +
          | key      | value    |
          + -------- + -------- +
          | lectures | lectures |
          | review   | review   |
          + -------- + -------- +

    """
    def _was_not_published(json):
        def _not_published(publication_info):
            return 'page_start' not in publication_info and 'artid' not in publication_info

        publication_infos = force_force_list(get_value(json, 'publication_info'))
        not_published = map(_not_published, publication_infos)

        return all(not_published)

    EXCLUSIVE_DOC_TYPE_MAP = {
        'published': 'peer reviewed',
        'thesis': 'thesis',
        'book': 'book',
        'bookchapter': 'book chapter',
        'proceedings': 'proceedings',
        'conferencepaper': 'conference paper',
        'note': 'note',
        'report': 'report',
        'activityreport': 'activity report',
    }

    INCLUSIVE_DOC_TYPE_MAP = {
        'lectures': 'lectures',
        'review': 'review',
    }

    if 'collections' not in json:
        json['facet_inspire_doc_type'] = []
        return

    result = []

    primary_collections = force_force_list(get_value(json, 'collections.primary'))
    normalized_collections = map(lambda el: el.lower(), primary_collections)

    for collection in normalized_collections:
        if collection in EXCLUSIVE_DOC_TYPE_MAP:
            result.append(EXCLUSIVE_DOC_TYPE_MAP[collection])
            break

    if not result:
        if _was_not_published(json):
            result.append('preprint')

    for collection in normalized_collections:
        if collection in INCLUSIVE_DOC_TYPE_MAP:
            result.append(INCLUSIVE_DOC_TYPE_MAP[collection])

    json['facet_inspire_doc_type'] = result


def match_valid_experiments(sender, json, *args, **kwargs):
    """Normalize the experiment names before indexing.

    FIXME: this is currently using a static Python dictionary, while it should
    use the current dynamic state of the Experiments collection.
    """
    def _normalize(experiment):
        try:
            result = EXPERIMENTS_MAP[experiment.lower().replace(' ', '')]
        except KeyError:
            result = experiment

        return result

    if 'accelerator_experiments' in json:
        accelerator_exps = json['accelerator_experiments']
        for accelerator_exp in accelerator_exps:
            facet_experiment = []
            if 'experiment' in accelerator_exp:
                experiments = force_force_list(accelerator_exp['experiment'])
                for experiment in experiments:
                    normalized_experiment = _normalize(experiment)
                    facet_experiment.append(normalized_experiment)
                accelerator_exp['facet_experiment'] = [facet_experiment]


def dates_validator(sender, json, *args, **kwargs):
    """Validate some dates in a record before indexing.

    Logs a warning if the value of a `date_key` in `DATE_KEYS_TO_CHECK` is
    invalid, as determined by the `create_valid_date` function. The valid
    value is substituted for the old value in all cases.
    """
    DATE_KEYS_TO_CHECK = [
        'opening_date',
        'closing_date',
        'deadline_date',
    ]

    for date_key in DATE_KEYS_TO_CHECK:
        if date_key in json:
            valid_date = create_valid_date(json[date_key])
            if valid_date != json[date_key]:
                current_app.logger.warning(
                    'MALFORMED: %s value in %s: %s', date_key,
                    json['control_number'], json[date_key])
            json[date_key] = valid_date


def references_validator(sender, json, *args, **kwargs):
    """Validate the recids in references before indexing.

    Logs a warning if the value corresponding to a `recid` key in `references`
    is not composed uniquely of digits. If it wasn't, it is also removed from
    its reference.
    """
    def _is_not_made_of_digits(recid):
        return not six.text_type(recid).isdigit()

    for reference in json.get('references', []):
        recid = reference.get('recid')
        if recid and _is_not_made_of_digits(recid):
            current_app.logger.warning(
                'MALFORMED: recid value found in references of %s: %s',
                json['control_number'], recid)
            del reference['recid']


def populate_recid_from_ref(sender, json, *args, **kwargs):
    """Extracts recids from all reference fields and adds them to ES.

    For every field that has as a value a reference object to another record,
    add a sibling after extracting the record id. e.g.
        {"record": {"$ref": "http://x/y/2}}
    is transformed to:
        {"record": {"$ref": "http://x/y/2},
         "recid": 2}
    Siblings are renamed using the following scheme:
        Remove "record" occurrences and append _recid without doubling or
        prepending underscores to the original name.

    For every known list of object references add a new list with the
    corresponding recids. e.g.
        {"records": [{"$ref": "http://x/y/1"}, {"$ref": "http://x/y/2"}]}
        is transformed to:
        {"records": [{"$ref": "http://x/y/1"}, {"$ref": "http://x/y/2"}]
         "recids": [1, 2]}
    """
    list_ref_fields_translations = {
        'deleted_records': 'deleted_recids'
    }

    def _recusive_find_refs(json_root):
        if isinstance(json_root, list):
            items = enumerate(json_root)
        elif isinstance(json_root, dict):
            # Note that items have to be generated before altering the dict.
            # In this case, iteritems might break during iteration.
            items = json_root.items()
        else:
            items = []

        for key, value in items:
            if (isinstance(json_root, dict) and isinstance(value, dict) and
                    '$ref' in value):
                # Append '_recid' and remove 'record' from the key name.
                key_basename = key.replace('record', '').rstrip('_')
                new_key = '{}_recid'.format(key_basename).lstrip('_')
                json_root[new_key] = get_recid_from_ref(value)
            elif (isinstance(json_root, dict) and isinstance(value, list) and
                    key in list_ref_fields_translations):
                new_list = [get_recid_from_ref(v) for v in value]
                new_key = list_ref_fields_translations[key]
                json_root[new_key] = new_list
            else:
                _recusive_find_refs(value)

    _recusive_find_refs(json)


def add_recids_and_validate(sender, json, *args, **kwargs):
    """Ensure that recids are generated before being validated."""
    populate_recid_from_ref(sender, json, *args, **kwargs)
    references_validator(sender, json, *args, **kwargs)


@before_record_update.connect
def check_if_record_is_going_to_be_deleted(sender, *args, **kwargs):
    """Checks if 'deleted' field is set as True before updating.

    If 'deleted' field exists and its value is True, before update,
    then delete all the record's pidstores.
    """
    control_number = int(sender.get('control_number'))
    collection = InspireRecordIdProvider.schema_to_pid_type(sender.get('$schema'))
    record = get_db_record(collection, control_number)

    if sender.get('deleted'):
        new_recid = get_recid_from_ref(sender.get('new_record'))
        if new_recid:
            merged_record = get_db_record(collection, new_recid)
            merge_pidstores_of_two_merged_records(merged_record.id, record.id)
        else:
            record = get_db_record(collection, control_number)
            soft_delete_pidstore_for_record(record.id)
