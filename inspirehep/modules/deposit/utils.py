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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from itertools import groupby
import collections


def filter_empty_helper(keys=None):
    """ Remove empty elements from a list."""
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and v:
                    return True
            return False
        else:
            return bool(elem)
    return _inner


DELETE_KEYS = ['type_of_doc',
               'fft',
               'acquisition_source',
               'collections',
               'ok_to_upload']

HIDDEN_INPUTS = ['categories_arXiv',
                 'title_crossref',
                 'title_arXiv',
                 'page_nr',
                 'conference_id',
                 'license_url',
                 'note',
                 'preprint_created']


def clean_unicode_keys(data):
    """Clean the unicode keys."""
    return [str(d.encode('utf-8')) for d in data]


def get_all_keys(dicts):
    """Get all keys from the dictionaries.

    return: A set() with all the keys combined.
    """
    all_keys = set()
    for d in dicts.values():
        # updates all keys
        all_keys |= set(d['categories'])
    return all_keys


def amend_all_keys(all_keys, dicts):
    """Add missing keys to metadata.

    Calculates the symmetric difference between the several metadata keys and
    adds the ones missing to the begining of the list. Then zips and sorts them.
    """
    for d in dicts.values():
        # symmetric difference
        missing = set(d['categories']) ^ all_keys
        d['categories'] += missing
        d['data'] += [0] * len(missing)
        categories, data = zip(*sorted(zip(d['categories'], d['data'])))
        d['categories'], d['data'] = list(humanize_keys(categories)), list(data)


def clean_unwanted_metadata(metadata_keys, metadata_values, include_hidden=False):
    """Remove keys that are not inputed by the user."""
    d = dict(zip(metadata_keys, metadata_values))
    for key in DELETE_KEYS:
        d.pop(key, None)
    if not include_hidden:
        for key in HIDDEN_INPUTS:
            d.pop(key, None)

    return d.keys(), d.values()


def humanize_keys(strings):
    """Humanize metadata keys.

    return: A dictionary comprehension with the keys.
    """
    return [string.replace('_', ' ').strip().title() for string in strings]


def process_metadata_for_charts(submitted_depositions, group_by=None, include_hidden=False):
    """Process the depositions metadata for charts.

    Gets all the submitted depositions (submissions with a sealed sip).

    return: A dict containing the raw depositions metadata, a dict with the
    metadata grouped by types, a dict with the metadata grouped and prepared for
    column charts and a list with all the metadata fields.
    """
    metadata = [d.get_latest_sip(sealed=True).metadata for d in submitted_depositions]
    metadata_by_types = {}
    metadata_for_column = {}
    metadata_categories = ['']
    c = collections.Counter()

    if group_by and metadata and group_by in metadata[0] and metadata[0][group_by]:
        for key, group in groupby(metadata, lambda x: x[group_by]):
            if str(key.encode('utf-8')).title() in metadata_by_types:
                metadata_by_types[str(key.encode('utf-8')).title()].extend(list(group))
            else:
                metadata_by_types[str(key.encode('utf-8')).title()] = list(group)

        for group_by in metadata_by_types:
            for deposition in metadata_by_types[group_by]:
                c.update(deposition.keys())
            categories, data = clean_unwanted_metadata(clean_unicode_keys(c.keys()),
                                                       c.values(),
                                                       include_hidden)
            metadata_by_types[group_by] = map(list, zip(humanize_keys(categories), data))
            metadata_for_column[group_by] = {'categories': categories,
                                             'name': group_by.title(),
                                             'data': data}
            c = collections.Counter()

        all_keys = get_all_keys(metadata_for_column)
        amend_all_keys(all_keys, metadata_for_column)
        try:
            metadata_categories = next(iter(metadata_for_column.values())).get('categories')
        except StopIteration:
            metadata_categories = ['']

    for deposition in metadata:
        c.update(deposition.keys())
    categories, data = clean_unwanted_metadata(clean_unicode_keys(c.keys()),
                                               c.values(),
                                               include_hidden)
    metadata = {'pie': map(list, zip(humanize_keys(categories), data)),
                'column': {'categories': list(humanize_keys(categories)),
                           'name': "Submitted depositions",
                           'data': data}
                }

    return dict(
        overall_metadata=metadata,
        stats=metadata_by_types,
        metadata_categories=metadata_categories,
        metadata_for_column=metadata_for_column,
    )
