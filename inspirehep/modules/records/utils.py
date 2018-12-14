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

""" Record related utils."""

from __future__ import absolute_import, division, print_function

from itertools import chain
from unicodedata import normalize
import re
import six

from inspire_dojson.utils import get_recid_from_ref
from inspire_utils.date import earliest_date
from inspire_utils.name import generate_name_variations, ParsedName
from inspire_utils.record import get_value
from inspire_utils.helpers import force_list

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_schema
)
from inspirehep.modules.records.errors import MissingInspireRecordError
from inspirehep.utils.record_getter import get_db_records
from inspire_utils.record import get_values_for_schema


def is_author(record):
    return 'authors.json' in record.get('$schema')


def is_hep(record):
    return 'hep.json' in record.get('$schema')


def is_data(record):
    return 'data.json' in record.get('$schema')


def is_institution(record):
    return 'institutions.json' in record.get('$schema')


def is_experiment(record):
    return 'experiments.json' in record.get('$schema')


def is_journal(record):
    return 'journals.json' in record.get('$schema')


def is_book(record):
    return 'book' in record.get('document_type', [])


def get_endpoint_from_record(record):
    """Return the endpoint corresponding to a record."""
    pid_type = get_pid_type_from_schema(record['$schema'])
    endpoint = get_endpoint_from_pid_type(pid_type)

    return endpoint


def get_pid_from_record_uri(record_uri):
    """Transform a URI to a record into a (pid_type, pid_value) pair."""
    parts = [part for part in record_uri.split('/') if part]
    try:
        pid_type = parts[-2][:3]
        pid_value = parts[-1]
    except IndexError:
        return None

    return pid_type, pid_value


def get_author_display_name(name):
    """Returns the display name in format Firstnames Lastnames"""
    parsed_name = ParsedName.loads(name)
    return " ".join(parsed_name.first_list + parsed_name.last_list)


def get_linked_records_in_field(record, field_path):
    """Get all linked records in a given field.

    Args:
        record (dict): the record containing the links
        field_path (string): a dotted field path specification understandable
            by ``get_value``, containing a json reference to another record.

    Returns:
        Iterator[dict]: an iterator on the linked record.

    Warning:
        Currently, the order in which the linked records are yielded is
        different from the order in which they appear in the record.

    Example:
        >>> record = {'references': [
        ...     {'record': {'$ref': 'https://labs.inspirehep.net/api/literature/1234'}},
        ...     {'record': {'$ref': 'https://labs.inspirehep.net/api/data/421'}},
        ... ]}
        >>> get_linked_record_in_field(record, 'references.record')
        [...]
    """
    full_path = '.'.join([field_path, '$ref'])
    pids = force_list([get_pid_from_record_uri(rec) for rec in get_value(record, full_path, [])])
    return get_db_records(pids)


def populate_earliest_date(record):
    """Populate the ``earliest_date`` field of Literature records."""
    date_paths = [
        'preprint_date',
        'thesis_info.date',
        'thesis_info.defense_date',
        'publication_info.year',
        'legacy_creation_date',
        'imprints.date',
    ]

    dates = [
        str(el) for el in chain.from_iterable(
            [force_list(get_value(record, path)) for path in date_paths]
        )
    ]

    if dates:
        result = earliest_date(dates)
        if result:
            record['earliest_date'] = result


def populate_citations_count(record):
    """Populate citations_count in ES from"""
    if hasattr(record, 'get_citations_count'):
        # Make sure that record has method get_citations_count
        # Session is in commited state here, and I cannot open new one...
        citation_count = record.get_citations_count()
        record['citation_count'] = citation_count
    else:
        raise MissingInspireRecordError("Record is not InspireRecord!")


def populate_bookautocomplete(record):
    """Populate the ```bookautocomplete`` field of Literature records."""
    paths = [
        'imprints.date',
        'imprints.publisher',
        'isbns.value',
    ]

    authors = force_list(get_value(record, 'authors.full_name', default=[]))
    titles = force_list(get_value(record, 'titles.title', default=[]))

    input_values = list(chain.from_iterable(
        force_list(get_value(record, path, default=[])) for path in paths))
    input_values.extend(authors)
    input_values.extend(titles)
    input_values = [el for el in input_values if el]

    record['bookautocomplete'] = {
        'input': input_values,
    }


def populate_inspire_document_type(record):
    """Populate the ``facet_inspire_doc_type`` field of Literature records."""
    result = []

    result.extend(record.get('document_type', []))
    result.extend(record.get('publication_type', []))
    if 'refereed' in record and record['refereed']:
        result.append('peer reviewed')

    record['facet_inspire_doc_type'] = result


def populate_recid_from_ref(record):
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
            if (isinstance(json_root, dict) and isinstance(value, dict) and '$ref' in value):
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

    _recursive_find_refs(record)


def populate_abstract_source_suggest(record):
    """Populate the ``abstract_source_suggest`` field in Literature records."""
    abstracts = record.get('abstracts', [])

    for abstract in abstracts:
        source = abstract.get('source')
        if source:
            abstract.update({
                'abstract_source_suggest': {
                    'input': source,
                },
            })


def populate_title_suggest(record):
    """Populate the ``title_suggest`` field of Journals records."""
    journal_title = get_value(record, 'journal_title.title', default='')
    short_title = record.get('short_title', '')
    title_variants = record.get('title_variants', [])

    input_values = []
    input_values.append(journal_title)
    input_values.append(short_title)
    input_values.extend(title_variants)
    input_values = [el for el in input_values if el]

    record['title_suggest'] = {
        'input': input_values,
    }


def populate_affiliation_suggest(record):
    """Populate the ``affiliation_suggest`` field of Institution records."""
    ICN = record.get('ICN', [])
    institution_acronyms = get_value(record, 'institution_hierarchy.acronym', default=[])
    institution_names = get_value(record, 'institution_hierarchy.name', default=[])
    legacy_ICN = record.get('legacy_ICN', '')
    name_variants = force_list(get_value(record, 'name_variants.value', default=[]))
    postal_codes = force_list(get_value(record, 'addresses.postal_code', default=[]))

    # XXX: this is need by the curators to search only with numbers
    extract_numbers_from_umr = []
    for name in name_variants:
        match = re.match(r'UMR\s', name, re.IGNORECASE)
        if match:
            umr_number = name.replace(match.group(0), '')
            extract_numbers_from_umr.append(umr_number)

    input_values = []
    input_values.extend(ICN)
    input_values.extend(institution_acronyms)
    input_values.extend(institution_names)
    input_values.append(legacy_ICN)
    input_values.extend(name_variants)
    input_values.extend(postal_codes)
    input_values.extend(extract_numbers_from_umr)
    input_values = [el for el in input_values if el]

    record['affiliation_suggest'] = {
        'input': input_values,
    }


def populate_experiment_suggest(record):
    """Populates experiment_suggest field of experiment records."""

    experiment_paths = [
        'accelerator.value',
        'collaboration.value',
        'experiment.short_name',
        'experiment.value',
        'institutions.value',
        'legacy_name',
        'long_name',
        'name_variants',
    ]

    input_values = [el for el in chain.from_iterable(
        [force_list(get_value(record, path)) for path in experiment_paths]) if el]

    record['experiment_suggest'] = {
        'input': input_values,
    }


def populate_name_variations(record):
    """Generate name variations for each signature of a Literature record."""
    authors = record.get('authors', [])

    for author in authors:
        full_name = author.get('full_name')
        if full_name:
            name_variations = generate_name_variations(full_name)

            author.update({'name_variations': name_variations})
            author.update({'name_suggest': {
                'input': [variation for variation in name_variations if variation],
            }})


def populate_number_of_references(record):
    """Generate name variations for each signature of a Literature record."""
    references = record.get('references')

    if references is not None:
        record['number_of_references'] = len(references)


def populate_authors_name_variations(record):
    """Generate name variations for an Author record."""
    author_name = get_value(record, 'name.value')

    if author_name:
        name_variations = generate_name_variations(author_name)
        record['name_variations'] = name_variations


def populate_author_count(record):
    """Populate the ``author_count`` field of Literature records."""
    authors = record.get('authors', [])

    authors_excluding_supervisors = [
        author for author in authors
        if 'supervisor' not in author.get('inspire_roles', [])
    ]
    record['author_count'] = len(authors_excluding_supervisors)


def populate_authors_full_name_unicode_normalized(record):
    """Populate the ``authors.full_name_normalized`` field of Literature records."""
    authors = record.get('authors', [])

    for index, author in enumerate(authors):
        full_name = six.text_type(author['full_name'])
        record['authors'][index].update({
            'full_name_unicode_normalized': normalize('NFKC', full_name).lower()
        })


def get_author_with_record_facet_author_name(author):
    author_ids = author.get('ids', [])
    author_bai = get_values_for_schema(author_ids, 'INSPIRE BAI')
    bai = author_bai[0] if author_bai else 'BAI'
    author_preferred_name = get_value(author, 'name.preferred_name')
    if author_preferred_name:
        return u'{}_{}'.format(bai, author_preferred_name)
    else:
        return u'{}_{}'.format(bai, get_author_display_name(author['name']['value']))


def populate_facet_author_name(record):
    """Populate the ``facet_author_name`` field of Literature records."""
    authors_with_record = get_linked_records_in_field(record, 'authors.record')
    authors_without_record = [author for author in record.get('authors', []) if 'record' not in author]
    result = []

    for author in authors_with_record:
        result.append(get_author_with_record_facet_author_name(author))

    for author in authors_without_record:
        result.append(u'BAI_{}'.format(get_author_display_name(author['full_name'])))

    record['facet_author_name'] = result


def populate_author_suggest(record, *args, **kwargs):
    """Populate the ``author_suggest`` field of Authors records."""
    author_paths = [
        'name.preferred_name',
        'name.previous_names',
        'name.name_variants',
        'name.native_names',
        'name.value',
    ]

    input_values = [el for el in chain.from_iterable([force_list(get_value(record, path)) for path in author_paths])]

    record['author_suggest'] = {
        'input': input_values
    }
