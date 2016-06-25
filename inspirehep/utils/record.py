# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Helpers for handling records."""

import re

SPLIT_KEY_PATTERN = re.compile('\.|\[')


def get_title(record):
    """Get preferred title from record."""
    chosen_title = ""

    for title in record.get('titles', []):
        if 'source' in title and title.get('source') != 'arXiv':
            return title.get('title')
        elif 'source' in title and title.get('source') == 'arXiv':
            pass
        else:
            chosen_title = title.get('title')

    if not chosen_title and len(record.get('titles', [])) > 0:
        chosen_title = record['titles'][0]['title']

    return chosen_title


def get_subtitle(record):
    """Get preferred subtitle from record."""
    chosen_subtitle = ""

    for title in record.get('titles', []):
        if 'source' in title and 'subtitle' in title and title.get('source') != 'arXiv':
            return title.get('subtitle')
        elif 'source' in title and 'subtitle' in title and title.get('source') == 'arXiv':
            if not chosen_subtitle:
                chosen_subtitle = title.get('subtitle')
        else:
            if 'subtitle' in title:
                chosen_subtitle = title.get('subtitle')
    return chosen_subtitle


def get_abstract(record):
    """Get preferred abstract from record."""
    chosen_abstract = ""

    for abstract in record.get('abstracts', []):
        if 'source' in abstract and abstract.get('source') != 'arXiv':
            return abstract.get('value')
        elif 'source' in abstract and abstract.get('source') == 'arXiv':
            pass
        else:
            chosen_abstract = abstract.get('value')

    if not chosen_abstract and len(record.get('abstracts', [])) > 0:
        chosen_abstract = record['abstracts'][0]['value']

    return chosen_abstract


def get_value(record, key, default=None):
    """Return item as `dict.__getitem__` but using 'smart queries'.
    .. note::
        Accessing one value in a normal way, meaning d['a'], is almost as
        fast as accessing a regular dictionary. But using the special
        name convention is a bit slower than using the regular access:
        .. code-block:: python
            >>> %timeit x = dd['a[0].b']
            100000 loops, best of 3: 3.94 us per loop
            >>> %timeit x = dd['a'][0]['b']
            1000000 loops, best of 3: 598 ns per loop
    """
    def getitem(k, v):
        if isinstance(v, dict):
            return v[k]
        elif ']' in k:
            k = k[:-1].replace('n', '-1')
            # Work around for list indexes and slices
            try:
                return v[int(k)]
            except ValueError:
                return v[slice(*map(
                    lambda x: int(x.strip()) if x.strip() else None,
                    k.split(':')
                ))]
        else:
            tmp = []
            for inner_v in v:
                try:
                    tmp.append(getitem(k, inner_v))
                except KeyError:
                    continue
            return tmp

    # Check if we are using python regular keys
    try:
        return record[key]
    except KeyError:
        pass

    keys = SPLIT_KEY_PATTERN.split(key)
    value = record
    for k in keys:
        try:
            value = getitem(k, value)
        except KeyError:
            return default
    return value


def is_submitted_but_not_published(record):
    """Return True if article is submitted to journal.

    Returns True if and only an article is submitted to a journal but has not
    yet been published (as far as we know).
    """
    def is_complete(publication_info):
        return (('journal_issue' in publication_info or
                 'journal_volume' in publication_info or
                 'year' in publication_info) and
                ('page_start' in publication_info or
                 'artid' in publication_info))
    if 'dois' in record:
        # DOIs exist, hence it's already published
        return False
    had_at_least_one_journal_title = False
    if 'publication_info' in record:
        for publication_info in record['publication_info']:
            if 'journal_title' in publication_info:
                had_at_least_one_journal_title = True
                if (publication_info['journal_title'].lower() in ('econf', ) and
                        'journal_volume' in publication_info):
                    # eConf are special
                    return False
                if is_complete(publication_info):
                    return False
    return had_at_least_one_journal_title
