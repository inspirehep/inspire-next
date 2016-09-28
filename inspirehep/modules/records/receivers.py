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

import json
import uuid

import requests
import six
from flask import current_app
from itertools import chain

from invenio_indexer.signals import before_record_index
from invenio_records.signals import before_record_insert, before_record_update

from inspirehep.dojson.utils import classify_field, get_recid_from_ref
from inspirehep.modules.authors.utils import author_tokenize
from inspirehep.utils.date import create_earliest_date, create_valid_date
from inspirehep.utils.helpers import force_force_list
from inspirehep.utils.record_getter import get_db_record
from inspirehep.utils.record import get_value, soft_delete_pidstore_for_record

from .experiments import EXPERIMENTS_MAP
from .signals import after_record_enhanced


#
# before_record_index
#

@before_record_index.connect
def earliest_date(sender, json, *args, **kwargs):
    """Find and assign the earliest date to a HEP paper."""
    date_paths = [
        'preprint_date',
        'thesis.date',
        'thesis.defense_date',
        'publication_info.year',
        'creation_modification_date.creation_date',
        'imprints.date',
    ]

    dates = list(chain.from_iterable(
        [force_force_list(get_value(json, path)) for path in date_paths]))

    earliest_date = create_earliest_date(dates)
    if earliest_date:
        json['earliest_date'] = earliest_date


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


def add_recids_and_validate(sender, json, *args, **kwargs):
    """Ensure that recids are generated before being validated."""
    populate_recid_from_ref(sender, json, *args, **kwargs)
    references_validator(sender, json, *args, **kwargs)


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


@before_record_index.connect
def generate_name_variations(recid, json, *args, **kwargs):
    """Adds a field with all the possible variations of an authors name.

    :param recid: The id of the record that is going to be indexed.
    :param json: The json representation of the record that is going to be
                 indexed.
    """
    authors = json.get("authors")
    if authors:
        for author in authors:
            name = author.get("full_name")
            if name:
                name_variations = author_tokenize(name)
                author.update({"name_variations": name_variations})
                bai = [
                    item['value'] for item in author.get('ids', [])
                    if item['type'] == 'INSPIRE BAI'
                ]
                author.update({"name_suggest": {
                    "input": name_variations,
                    "output": name,
                    "payload": {"bai": bai[0] if bai else None}
                }})


#
# before_record_update
#

@before_record_update.connect
def check_if_record_is_going_to_be_deleted(sender, *args, **kwargs):
    """Checks if 'deleted' field is set as True before updating.

    If 'deleted' field exists and its value is True, before update,
    then delete all the record's pidstores.
    """
    if sender.get('deleted'):
        record = get_db_record('literature', int(sender.get('control_number')))
        soft_delete_pidstore_for_record(record.id)


#
# before_record_update & before_record_insert
#

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
    """
    def _is_normalized(field):
        scheme_is_inspire = field.get('scheme') == 'INSPIRE'
        return scheme_is_inspire or '_scheme' in field or '_term' in field

    def _is_from_inspire(term):
        return term and term != 'Other'

    for i, field in enumerate(sender.get('field_categories', [])):
        if _is_normalized(field):
            continue

        original_term = field.get('term')
        normalized_term = classify_field(original_term)
        scheme = 'INSPIRE' if _is_from_inspire(normalized_term) else None

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


@before_record_insert.connect
@before_record_update.connect
def assign_phonetic_block(sender, *args, **kwargs):
    """Assign phonetic block to each signature.

    The method extends the given signature with a phonetic
    notation of the author's full name, based on
    nysiis algorithm. The phonetic block is assigned before
    the signature is indexed by an Elasticsearch instance.
    """
    if current_app.config.get('BEARD_API_URL'):
        authors = sender.get('authors', [])
        authors_map = {}

        for index, author in enumerate(authors):
            if 'full_name' in author:
                authors_map[author['full_name']] = index

        # Call Beard API to generate phonetic blocks.
        signatures_blocks = _query_beard_api(authors_map.keys())

        # Add signature block to an author.
        for full_name, signature_block in signatures_blocks.iteritems():
            authors[authors_map[full_name]].update(
                {"signature_block": signature_block})

        # # For missing phonetic blocks (not valid full names) add None.
        for full_name in list(
                set(authors_map.keys()) - set(signatures_blocks.keys())):
            authors[authors_map[full_name]].update(
                {"signature_block": None})


def _query_beard_api(full_names):
    """Query Beard API.

    This method allows for computation of phonetic blocks
    from a given list of strings.
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    text_endpoint = "{base_url}/text/phonetic_blocks".format(
        base_url=current_app.config.get('BEARD_API_URL')
    )

    response = requests.post(
        url=text_endpoint,
        headers=headers,
        data=json.dumps({'full_names': full_names})
    )

    return response.json()['phonetic_blocks']


@before_record_insert.connect
@before_record_update.connect
def assign_uuid(sender, *args, **kwargs):
    """Assign uuid to each signature.
    The method assigns to each signature a universally unique
    identifier based on Python's built-in uuid4. The identifier
    is allocated during the insertion of a new record.
    """
    authors = sender.get('authors', [])

    for author in authors:
        # Skip if the author was already populated with a UUID.
        if 'uuid' not in author:
            author['uuid'] = str(uuid.uuid4())
