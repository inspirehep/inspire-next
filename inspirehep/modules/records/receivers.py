# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Records receivers."""

from __future__ import absolute_import, division, print_function

import uuid
from itertools import chain

import six
from flask import current_app
from flask_sqlalchemy import models_committed

from invenio_indexer.api import RecordIndexer
from invenio_indexer.signals import before_record_index
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from invenio_records.signals import (
    before_record_insert,
    before_record_update,
)

from inspire_dojson.utils import get_recid_from_ref
from inspire_utils.helpers import force_list
from inspire_utils.record import get_value
from inspirehep.modules.authors.utils import author_tokenize, phonetic_blocks
from inspirehep.utils.date import create_earliest_date


#
# before_record_insert & before_record_update
#

@before_record_insert.connect
@before_record_update.connect
def assign_phonetic_block(sender, *args, **kwargs):
    """Assign a phonetic block to each signature of a Literature record.

    Uses the NYSIIS algorithm to compute a phonetic block from each
    signature's full name, skipping those that are not recognized
    as real names, but logging an error when that happens.
    """
    authors = sender.get('authors', [])

    authors_map = {}
    for i, author in enumerate(authors):
        if 'full_name' in author:
            authors_map[author['full_name']] = i

    try:
        signatures_blocks = phonetic_blocks(authors_map.keys())
    except Exception as err:
        current_app.logger.error(
            'Cannot extract phonetic blocks for record %d: %s',
            sender.get('control_number'), err)
        return

    for full_name, signature_block in six.iteritems(signatures_blocks):
        authors[authors_map[full_name]].update({
            'signature_block': signature_block,
        })


@before_record_insert.connect
@before_record_update.connect
def assign_uuid(sender, *args, **kwargs):
    """Assign a UUID to each signature of a Literature record."""
    authors = sender.get('authors', [])

    for author in authors:
        if 'uuid' not in author:
            author['uuid'] = str(uuid.uuid4())


#
# models_committed
#

@models_committed.connect
def index_after_commit(sender, changes):
    """Index a record in ES after it was committed to the DB.

    This cannot happen in an ``after_record_commit`` receiver from Invenio-Records
    because, despite the name, at that point we are not yet sure whether the record
    has been really committed to the DB.
    """
    indexer = RecordIndexer()

    for model_instance, change in changes:
        if isinstance(model_instance, RecordMetadata):
            if change in ('insert', 'update'):
                indexer.index(Record(model_instance.json, model_instance))
            else:
                indexer.delete(Record(model_instance.json, model_instance))


#
# before_record_index
#

@before_record_index.connect
def add_book_autocomplete(sender, json, *args, **kwargs):
    """Populate the ```bookautocomplete`` field of Literature records."""
    if 'book' not in json.get('document_type', []):
        return

    authors = force_list(get_value(json, 'authors.full_name'))
    titles = force_list(get_value(json, 'titles.title'))

    result = json.get('bookautocomplete', [])
    result.extend(authors)
    result.extend(titles)

    ref = get_value(json, 'self.$ref')

    json.update({
        'bookautocomplete': {
            'input': result,
            'payload': {
                'authors': authors,
                'id': ref,
                'title': titles,
            },
        },
    })


@before_record_index.connect
def populate_inspire_document_type(sender, json, *args, **kwargs):
    """Populate the ``facet_inspire_doc_type`` field of Literature records."""
    result = []

    result.extend(json.get('document_type', []))
    result.extend(json.get('publication_type', []))
    if 'refereed' in json and json['refereed']:
        result.append('peer reviewed')

    json['facet_inspire_doc_type'] = result


@before_record_index.connect
def populate_recid_from_ref(sender, json, *args, **kwargs):
    """Extract recids from all JSON reference fields and add them to ES.

    For every field that has as a value a JSON reference, adds a sibling
    after extracting the record identifier. Siblings are named by removing
    ``record`` occurrences and appending ``_recid`` without doubling or
    prepending underscores to the original name.

    Example::

        {'record': {'$ref': 'http://x/y/2}}

    is transformed to::

        {
            'recid': 2,
            'record': {'$ref': 'http://x/y/2},
        }

    For every list of object references adds a new list with the
    corresponding recids, whose name is similarly computed.

    Example::

        {
            'records': [
                {'$ref': 'http://x/y/1'},
                {'$ref': 'http://x/y/2'},
            ],
        }

    is transformed to::

        {
            'recids': [1, 2],
            'records': [
                {'$ref': 'http://x/y/1'},
                {'$ref': 'http://x/y/2'},
            ],
        }

    """
    list_ref_fields_translations = {
        'deleted_records': 'deleted_recids'
    }

    def _recursive_find_refs(json_root):
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
                _recursive_find_refs(value)

    _recursive_find_refs(json)


@before_record_index.connect
def populate_abstract_source_suggest(sender, json, *args, **kwargs):
    """Populate the ``abstract_source_suggest`` field in Literature records."""
    if 'hep.json' not in json.get('$schema'):
        return

    abstracts = json.get('abstracts', [])

    for abstract in abstracts:
        source = abstract.get('source')
        if source:
            abstract.update({
               'abstract_source_suggest': {
                   'input': source,
                   'output': source,
               },
            })


@before_record_index.connect
def populate_title_suggest(sender, json, *args, **kwargs):
    """Populate the ``title_suggest`` field of Journals records."""
    if 'journals.json' not in json.get('$schema'):
        return

    journal_title = get_value(json, 'journal_title.title', default='')
    short_title = json.get('short_title', '')
    title_variants = json.get('title_variants', [])

    input_values = []
    input_values.append(journal_title)
    input_values.append(short_title)
    input_values.extend(title_variants)
    input_values = [el for el in input_values if el]

    json.update({
        'title_suggest': {
            'input': input_values,
            'output': short_title if short_title else '',
            'payload': {
                'full_title': journal_title if journal_title else '',
            },
        }
    })


@before_record_index.connect
def populate_affiliation_suggest(sender, json, *args, **kwargs):
    """Populate the ``affiliation_suggest`` field of Institution records."""
    if 'institutions.json' not in json.get('$schema'):
        return

    ICN = json.get('ICN', [])
    institution_acronyms = get_value(json, 'institution_hierarchy.acronym', default=[])
    institution_names = get_value(json, 'institution_hierarchy.name', default=[])
    legacy_ICN = json.get('legacy_ICN', '')
    name_variants = force_list(get_value(json, 'name_variants.value', default=[]))
    postal_codes = force_list(get_value(json, 'addresses.postal_code', default=[]))

    input_values = []
    input_values.extend(ICN)
    input_values.extend(institution_acronyms)
    input_values.extend(institution_names)
    input_values.append(legacy_ICN)
    input_values.extend(name_variants)
    input_values.extend(postal_codes)
    input_values = [el for el in input_values if el]

    json.update({
        'affiliation_suggest': {
            'input': input_values,
            'output': legacy_ICN,
            'payload': {
                '$ref': get_value(json, 'self.$ref'),
                'ICN': ICN,
                'institution_acronyms': institution_acronyms,
                'institution_names': institution_names,
                'legacy_ICN': legacy_ICN,
            },
        },
    })


@before_record_index.connect
def earliest_date(sender, json, *args, **kwargs):
    """Populate the ``earliest_date`` field of Literature records."""
    date_paths = [
        'preprint_date',
        'thesis_info.date',
        'thesis_info.defense_date',
        'publication_info.year',
        'legacy_creation_date',
        'imprints.date',
    ]

    dates = list(chain.from_iterable(
        [force_list(get_value(json, path)) for path in date_paths]))

    earliest_date = create_earliest_date(dates)
    if earliest_date:
        json['earliest_date'] = earliest_date


@before_record_index.connect
def generate_name_variations(sender, json, *args, **kwargs):
    """Generate name variations for each signature of a Literature record."""
    authors = json.get('authors', [])

    for author in authors:
        full_name = author.get('full_name')
        if full_name:
            bais = [
                el['value'] for el in author.get('ids', [])
                if el['schema'] == 'INSPIRE BAI'
            ]
            name_variations = author_tokenize(full_name)

            author.update({'name_variations': name_variations})
            author.update({'name_suggest': {
                'input': name_variations,
                'output': full_name,
                'payload': {'bai': bais[0] if bais else None}
            }})
