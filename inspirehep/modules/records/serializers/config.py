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


MAX_AUTHORS_BEFORE_ET_AL = 10  # According to CSE stylebook.
"""Maximum number of authors to be displayed without truncation.

Note:

    For more than ``MAX_AUTHORS_BEFORE_ET_AL`` only the first author should be displayed
    and a suitable truncation method is applied.

"""


COMMON_FIELDS_FOR_ENTRIES = [
    'key', 'SLACcitation', 'archivePrefix', 'doi', 'eprint', 'month', 'note', 'primaryClass', 'title', 'url', 'year'
]
"""BibTeX fields shared among all bibtex entries."""


FIELDS_FOR_ENTRY_TYPE = {
    'techreport': [
        'author', 'collaboration', 'number', 'address', 'type', 'institution'
    ],
    'phdthesis': [
        'reportNumber', 'school', 'address', 'type', 'author'
    ],
    'inproceedings': [
        'publisher', 'author', 'series', 'booktitle', 'number', 'volume', 'reportNumber', 'editor', 'address',
        'organization', 'pages'
    ],
    'misc': [
        'howpublished', 'reportNumber', 'author'
    ],
    'mastersthesis': [
        'reportNumber', 'school', 'address', 'type', 'author'
    ],
    'proceedings': [
        'publisher', 'series', 'number', 'volume', 'reportNumber', 'editor', 'address', 'organization', 'pages'
    ],
    'book': [
        'publisher', 'isbn', 'author', 'series', 'number', 'volume', 'edition', 'editor', 'reportNumber', 'address'
    ],
    'inbook': [
        'chapter', 'publisher', 'author', 'series', 'number', 'volume', 'edition', 'editor', 'reportNumber',
        'address', 'type', 'pages'
    ],
    'article': [
        'author', 'journal', 'collaboration', 'number', 'volume', 'reportNumber', 'pages'
    ],
}
"""Specific fields for a given bibtex entry.

Note:

    Since we're trying to match as many as possible
    it doesn't matter whether they're mandatory or optional

"""
