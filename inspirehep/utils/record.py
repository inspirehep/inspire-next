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

from __future__ import absolute_import, division, print_function

from itertools import chain

from inspire_utils.record import get_value


def get_abstract(record):
    """Return the first abstract of a record.

    Args:
        record (InspireRecord): a record.

    Returns:
        str: the first abstract of the record.

    Examples:
        >>> record = {
        ...     'abstracts': [
        ...         {
        ...             'source': 'arXiv',
        ...             'value': 'Probably not.',
        ...         },
        ...     ],
        ... }
        >>> get_abstract(record)
        'Probably not.'

    """
    return get_value(record, 'abstracts.value[0]', default='')


def get_arxiv_categories(record):
    """Return all the arXiv categories of a record.

    Args:
        record (InspireRecord): a record.

    Returns:
        list(str): all the arXiv categories of the record.

    Examples:
        >>> record = {
        ...     'arxiv_eprints': [
        ...         {
        ...             'categories': [
        ...                 'hep-th',
        ...                 'hep-ph',
        ...             ],
        ...             'value': '1612.08928',
        ...         },
        ...     ],
        ... }
        >>> get_arxiv_categories(record)
        ['hep-th', 'hep-ph']

    """
    return list(chain.from_iterable(
        get_value(record, 'arxiv_eprints.categories', default=[])))


def get_arxiv_id(record):
    """Return the first arXiv identifier of a record.

    Args:
        record (InspireRecord): a record.

    Returns:
        str: the first arXiv identifier of the record.

    Examples:
        >>> record = {
        ...     'arxiv_eprints': [
        ...         {
        ...             'categories': [
        ...                 'hep-th',
        ...                 'hep-ph',
        ...             ],
        ...             'value': '1612.08928',
        ...         },
        ...     ],
        ... }
        >>> get_arxiv_id(record)
        '1612.08928'

    """
    return get_value(record, 'arxiv_eprints.value[0]', default='')


def get_source(record):
    """Return the acquisition source of a record.

    Args:
        record (InspireRecord): a record.

    Returns:
        str: the acquisition source of the record.

    Examples:
        >>> record = {
        ...     'acquisition_source': {
        ...         'method': 'oai',
        ...         'source': 'arxiv',
        ...     }
        ... }
        >>> get_source(record)
        'arxiv'

    """
    return get_value(record, 'acquisition_source.source', default='')


def get_subtitle(record):
    """Return the first subtitle of a record.

    Args:
        record (InspireRecord): a record.

    Returns:
        str: the first subtitle of the record.

    Examples:
        >>> record = {
        ...     'titles': [
        ...         {
        ...             'subtitle': 'A mathematical exposition',
        ...             'title': 'The General Theory of Relativity',
        ...         },
        ...     ],
        ... }
        >>> get_subtitle(record)
        'A mathematical exposition'

    """
    return get_value(record, 'titles.subtitle[0]', default='')


def get_title(record):
    """Return the first title of a record.

    Args:
        record (InspireRecord): a record.

    Returns:
        str: the first title of the record.

    Examples:
        >>> record = {
        ...     'titles': [
        ...         {
        ...             'subtitle': 'A mathematical exposition',
        ...             'title': 'The General Theory of Relativity',
        ...         },
        ...     ],
        ... }
        >>> get_title(record)
        'The General Theory of Relativity'

    """
    return get_value(record, 'titles.title[0]', default='')
