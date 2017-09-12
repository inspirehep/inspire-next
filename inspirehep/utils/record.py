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

"""Helpers for handling records."""

from __future__ import absolute_import, division, print_function

from itertools import chain

from inspire_utils.record import get_value


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


def get_arxiv_categories(record):
    """Return all the arXiv categories of a record.

    Args:
        record: a record.

    Returns:
        list: all the arXiv categories of the record.

    Examples:
        >>> record = {'arxiv_eprints': [{'categories': ['hep-ph', 'hep-th']}]}
        >>> get_arxiv_categories(record)
        ['hep-ph', 'hep-th']

    """
    return list(chain.from_iterable(
        get_value(record, 'arxiv_eprints.categories', default=[])))


def get_arxiv_id(record):
    """Return the first arXiv identifier of a record."""
    return get_value(record, 'arxiv_eprints.value[0]', default='')


def get_subtitle(record):
    """Get preferred subtitle from record."""
    return get_value(record, 'titles.subtitle[0]', default='')


def get_title(record):
    """Get preferred title from record."""
    return get_value(record, 'titles.title[0]', default='')


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


def get_source(record):
    """Return the ``source`` of ``acquisition_source`` of a record."""
    return get_value(record, 'acquisition_source.source')
