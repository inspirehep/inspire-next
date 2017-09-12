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
from .extractor import make_extractor


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

# Fields for a given bibtex entry. Since we're trying to match as many as possible
# it doesn't matter w/e they're mandatory or optional
FIELDS_FOR_ENTRY_TYPE = {
    'article': ['author', 'collaboration', 'journal', 'month', 'note', 'number', 'pages', 'title', 'volume', 'year',
                'reportNumber', 'doi', 'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation', 'url'],
    'book': ['address', 'author', 'edition', 'editor', 'month', 'note', 'number', 'publisher', 'series', 'title',
             'volume', 'year', 'reportNumber', 'doi', 'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation',
             'isbn', 'url'],
    'inbook': ['address', 'author', 'chapter', 'edition', 'editor', 'month', 'note', 'number', 'pages', 'publisher',
               'series', 'title', 'type', 'volume', 'year', 'reportNumber', 'doi', 'archivePrefix', 'eprint',
               'primaryClass', 'SLACcitation', 'url'],
    'inproceedings': ['address', 'author', 'booktitle', 'editor', 'month', 'note', 'number', 'pages', 'organization',
                   'publisher', 'series', 'title', 'volume', 'year', 'reportNumber', 'doi', 'archivePrefix', 'eprint',
                   'primaryClass', 'SLACcitation', 'url'],
    'proceedings': ['address', 'editor', 'month', 'note', 'number', 'organization', 'pages', 'publisher', 'series',
                    'title', 'volume', 'year', 'reportNumber', 'doi', 'archivePrefix', 'eprint', 'primaryClass',
                    'SLACcitation', 'url'],
    'techreport': ['address', 'author', 'collaboration', 'institution', 'month', 'note', 'number', 'title', 'type',
                   'year', 'doi', 'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation', 'url'],
    'phdthesis': ['address', 'author', 'month', 'note', 'school', 'title', 'type', 'year', 'reportNumber', 'doi',
                  'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation', 'url'],
    'mastersthesis': ['address', 'author', 'month', 'note', 'school', 'title', 'type', 'year', 'reportNumber', 'doi',
                      'archivePrefix', 'eprint', 'primaryClass', 'SLACcitation', 'url'],
    'misc': ['author', 'howpublished', 'month', 'note', 'title', 'year', 'reportNumber', 'doi', 'archivePrefix',
             'eprint', 'primaryClass', 'SLACcitation', 'url']
}


def bibtex_document_type(doc_type, obj):
    """
    Returns a bibtex document type for an entry.
    :param doc_type: INSPIRE document type.
    :param obj: Object preloaded by schema.
    :return: Bibtex document type.
    """
    if doc_type in DOCUMENT_TYPE_MAP:
        return DOCUMENT_TYPE_MAP[doc_type]
    # Theses need special treatment, because bibtex differentiates between their types:
    elif doc_type == 'thesis' and obj['thesis_info']['degree_type'] == 'phd':
        return 'phdthesis'
    elif doc_type == 'thesis' and obj['thesis_info']['degree_type'] == 'master':
        return 'mastersthesis'
    # Other types of theses (other, diploma, bachelor, laurea, habilitation) don't have separate types in bibtex:
    elif doc_type == 'thesis':
        return 'misc'  # TODO: maybe use mastersthesis with a type specifying the degree?
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


extractor = make_extractor()


def get_authors_with_role(authors, role):
    """
    Extract names of people from an authors field given their roles.
    :param authors: Authors field of the record.
    :param role: String specifying the role 'author', 'editor', etc.
    :return: List of names of people.
    """
    filtered = []
    for author in authors:
        if 'inspire_roles' in author and role in author['inspire_roles']:
            filtered.append(author['full_name'])
        elif 'inspire_roles' not in author and role == 'author':
            filtered.append(author['full_name'])
    return filtered


def eprint_new_style(eprint):
    """
    Given an arXiv eprint sting detect new (1234.5678) vs old style (hep-ph/123456)
    :param eprint: Eprint string.
    :return: True if new style, else False.
    """
    return '/' not in eprint and ' ' not in eprint


def get_publication_info(data):
    """
    Get publication_info field from data.
    :param data: Pre-loaded record.
    :return: Return publication_info field if exists, else empty dictionary.
    """
    return data.get('publication_info', {})

# Functions below describe where the non-obvious data is located


@extractor('author')
def get_author(data, doc_type):
    """
    Note: Only used to generate author field if corporate_author is the author.
    """
    if 'corporate_author' in data:
        return ', '.join(data['corporate_author'])


@extractor('journal')
def get_journal(data, doc_type):
    return get_publication_info(data).get('journal')


@extractor('volume')
def get_volume(data, doc_type):
    return get_publication_info(data).get('volume')


@extractor('year')
def get_year(data, doc_type):
    if 'publication_info' in data and 'year' in data['publication_info'] \
            and not (doc_type.endswith('thesis') and 'thesis_info' in data):
        return data['publication_info']['year']
    if 'thesis_info' in data and 'date' in data['thesis_info']:
        return data['thesis_info']['date'][0]
    if 'imprints' in data and 'date' in data['imprints']:
        return data['imprints']['date'][0]


@extractor('number')
def get_number(data, doc_type):
    return get_publication_info(data).get('number')


@extractor('pages')
def get_pages(data, doc_type):
    pub_info = get_publication_info(data)
    page_start, page_end = pub_info.get('page_start'), pub_info.get('page_end')
    if page_start and page_end:
        return "{}--{}".format(page_start, page_end)


@extractor('primaryClass')
def get_primary_class(data, doc_type):
    categories = data.get('arxiv_eprints', {}).get('categories', [])
    if len(categories) > 0:
        return categories[0]


@extractor('eprint')
def get_eprint(data, doc_type):
    return data.get('arxiv_eprints', {}).get('value')


@extractor('archivePrefix')
def get_arxiv_prefix(data, doc_type):
    if data.get('arxiv_eprints', {}).get('value'):
        return "arXiv"


@extractor('SLACcitation')
def get_slac_citation(data, doc_type):
    source = ""
    eprint = data.get('arxiv_eprints', {}).get('value')
    if not eprint and data.get('reportNumber', []):
        source = data['reportNumber'][0]
    elif eprint and eprint_new_style(eprint):
        source = "ARXIV:" + eprint
    elif eprint:
        source = eprint
    elif 'doi' in data:
        source = 'doi:' + data['doi']
    # else:
    #     source = "INSPIRE-" + str(data['key'])

    if source:
        return "%%CITATION = {};%%".format(source).upper()


@extractor('school')
def get_school(data, doc_type):
    schools = data.get('thesis_info', {}).get('institutions', [])
    if schools:
        return ', '.join(schools)


@extractor('address')
def get_address(data, doc_type):
    pubinfo_address = get_publication_info(data).get('conference', {}).get('address')
    imprint_address = data.get('imprints', {}).get('place')
    return pubinfo_address or imprint_address


@extractor('booktitle')
def get_booktitle(data, doc_type):
    return get_publication_info(data).get('conference', {}).get('title')


@extractor('publisher')
def get_publisher(data, doc_type):
    return data.get('imprints', {}).get('publisher')


@extractor('reportNumber')
def get_report_number(data, doc_type):
    if data.get('reportNumber', []):
        return ', '.join(data.get('reportNumber', []))


@extractor('isbn')
def get_isbn(data, doc_type):
    if 'isbn' in data:
        return ', '.join(data['isbn'])
