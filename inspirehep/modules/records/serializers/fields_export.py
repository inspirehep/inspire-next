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

"""Instructions on where to find relevant bits of data in API."""

from __future__ import absolute_import, division, print_function


MAX_AUTHORS_BEFORE_ET_AL = 10  # According to CSE stylebook

DOCUMENT_TYPE_MAP = {
    'article': 'article',
    'book': 'book',
    'book chapter': 'inbook',
    'conference paper': 'inproceedings',
    'proceedings': 'proceedings',
    'report': 'techreport',
    'note': 'article',
    # theses handled separately due to masters/phd distinction
}

FIELDS_FOR_ENTRY_TYPE = {
    'article': ['author', 'collaboration', 'journal', 'month', 'note', 'number', 'pages', 'title', 'volume', 'year',
                'doi', 'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation'],
    'book': ['address', 'author', 'edition', 'editor', 'month', 'note', 'number', 'publisher', 'series', 'title',
             'volume', 'year', 'doi', 'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation', 'isbn'],
    'inbook': ['address', 'author', 'chapter', 'edition', 'editor', 'month', 'note', 'number', 'pages', 'publisher',
               'series', 'title', 'type', 'volume', 'year', 'doi', 'archivePrefix', 'eprint', 'primaryClass',
               'SLACcitation'],
    'inproceedings': ['address', 'author', 'booktitle', 'editor', 'month', 'note', 'number', 'pages', 'organization',
                   'publisher', 'series', 'title', 'volume', 'year', 'doi', 'archivePrefix', 'eprint', 'primaryClass',
                   'SLACcitation'],
    'proceedings': ['address', 'editor', 'month', 'note', 'number', 'organization', 'title', 'year'],
    'techreport': ['address', 'author', 'collaboration', 'institution', 'month', 'note', 'number', 'title', 'type',
                   'year', 'doi', 'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation'],
    'phdthesis': ['address', 'author', 'month', 'note', 'school', 'title', 'type', 'year', 'reportNumber', 'doi',
                  'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation'],
    'mastersthesis': ['address', 'author', 'month', 'note', 'school', 'title', 'type', 'year', 'reportNumber', 'doi',
                      'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation'],
    'misc': ['author', 'howpublished', 'month', 'note', 'title', 'year', 'doi', 'archivePrefix', 'eprint',
             'primaryClass', 'SLACcitation']
}


def bibtex_document_type(doc_type, obj):
    """Returns a bibtex document type for an entry."""
    if doc_type in DOCUMENT_TYPE_MAP:
        return DOCUMENT_TYPE_MAP[doc_type]
    # Theses need special treatment, because bibtex differentiates between their types:
    elif doc_type == 'thesis' and obj['thesis_info']['degree_type'] == 'phd':
        return 'phdthesis'
    elif doc_type == 'thesis' and obj['thesis_info']['degree_type'] == 'master':
        return 'mastersthesis'
    # Other types of theses (other, diploma, bachelor, laurea, habilitation) don't have separate types in bibtex:
    elif doc_type == 'thesis':
        return 'misc'
    # Report numbers imply report type
    # elif doc_type == 'note' and 'report_numbers' in obj:
    #     return 'techreport'
    else:
        return 'misc'


def bibtex_type_and_fields(data):
    """Returns a bibtex document type and fields for an entry."""
    bibtex_doc_types = []
    for idx, doc_type in enumerate(data['document_type']):
        bibtex_doc_types.append(bibtex_document_type(doc_type, data))

    # Preference towards article, as it's more prestigious to have sth published
    if 'article' in bibtex_doc_types:
        return 'article', FIELDS_FOR_ENTRY_TYPE['article']

    bibtex_doc_type = bibtex_doc_types[0] if bibtex_doc_types else 'misc'
    return bibtex_doc_type, FIELDS_FOR_ENTRY_TYPE[bibtex_doc_type]


def make_author_list(authors):
    if len(authors) <= MAX_AUTHORS_BEFORE_ET_AL:
        return ' and '.join(authors)
    else:
        return authors[0] + ' and others'


def make_extractor():
    store = {}

    def extractor(field):
        def decorator(fun):
            store[field] = fun
            return fun
        return decorator
    extractor.store = store
    return extractor


extractor = make_extractor()

# Functions below describe where the non-obvious data is located


@extractor('author')
def get_author(data, doc_type):
    authors = make_author_list(data.get('author', []))
    corporate_authors = make_author_list(data.get('corporate_author', []))
    return authors or corporate_authors


def get_publication_info(data):
    return data.get('publication_info', {})


@extractor('journal')
def get_journal(data, doc_type):
    return get_publication_info(data).get('journal')


@extractor('volume')
def get_volume(data, doc_type):
    return get_publication_info(data).get('volume')


@extractor('year')
def get_year(data, doc_type):
    if get_publication_info(data):
        return data['publication_info'].get('year')
    if 'thesis_info' in data and 'date' in data['thesis_info']:
        return data['thesis_info']['date']
    if data.get('preprint_date'):
        return data['preprint_date'][0]
    if data.get('earliest_date'):
        return data['earliest_date'][0]


@extractor('number')
def get_number(data, doc_type):
    return get_publication_info(data).get('number')


@extractor('pages')
def get_pages(data, doc_type):
    pub_info = get_publication_info(data)
    page_start, page_end = pub_info.get('page_start'), pub_info.get('page_end')
    if page_start and page_end:
        return "{} -- {}".format(page_start, page_end)


@extractor('primaryClass')
def get_primary_class(data, doc_type):
    categories = data.get('arxiv_eprints', {}).get('categories', [])
    if len(categories) > 0:
        return categories[0]


@extractor('eprint')
def get_eprint(data, doc_type):
    return data.get('arxiv_eprints', {}).get('value')


@extractor('SLACcitation')
def get_slac_citation(data, doc_type):
    eprint = data.get('arxiv_eprints', {}).get('value')
    if not eprint:
        return data.get('reportNumber')

    if '/' in eprint or ' ' in eprint:  # old style, TODO: fix very crude check
        return eprint
    else:  # new style
        return "ARXIV:" + eprint

@extractor('school')
def get_school(data, doc_type):
    return make_author_list(data.get('thesis_info', {}).get('institutions', []))

@extractor('address')
def get_address(data, doc_type):
    return get_publication_info(data).get('conference', {}).get('address')

@extractor('booktitle')
def get_booktitle(data, doc_type):
    return get_publication_info(data).get('conference', {}).get('title')