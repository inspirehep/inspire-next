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
from idutils import is_arxiv_post_2007
from inspire_utils.record import get_value


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

# Fields shared among all bibtex entries:
COMMON_FIELDS_FOR_ENTRIES = ['SLACcitation', 'archivePrefix', 'doi', 'eprint', 'month', 'note', 'primaryClass',
                             'title', 'url', 'year']

# Fields for a given bibtex entry. Since we're trying to match as many as possible
# it doesn't matter w/e they're mandatory or optional
FIELDS_FOR_ENTRY_TYPE = {
    'techreport': ['author', 'collaboration', 'number', 'address', 'type', 'institution'],
    'phdthesis': ['reportNumber', 'school', 'address', 'type', 'author'],
    'inproceedings': ['publisher', 'author', 'series', 'booktitle', 'number', 'volume', 'reportNumber', 'editor',
                      'address', 'organization', 'pages'],
    'misc': ['howpublished', 'reportNumber', 'author'],
    'mastersthesis': ['reportNumber', 'school', 'address', 'type', 'author'],
    'proceedings': ['publisher', 'series', 'number', 'volume', 'reportNumber', 'editor', 'address', 'organization',
                    'pages'],
    'book': ['publisher', 'isbn', 'author', 'series', 'number', 'volume', 'edition', 'editor', 'reportNumber',
             'address'],
    'inbook': ['chapter', 'publisher', 'author', 'series', 'number', 'volume', 'edition', 'editor', 'reportNumber',
               'address', 'type', 'pages'],
    'article': ['author', 'journal', 'collaboration', 'number', 'volume', 'reportNumber', 'pages'],
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
    # Other types of theses (other, diploma, bachelor, laurea, habilitation) don't have separate types in bibtex:
    # We will use the type field (see `get_type`) to indicate the type of diploma.
    elif doc_type == 'thesis':
        return 'mastersthesis'
    return 'misc'


def bibtex_type_and_fields(data):
    """Returns a bibtex document type and fields for an entry."""
    bibtex_doc_types = [bibtex_document_type(doc_type, data) for doc_type in data['document_type']] + ['misc']
    # Preference towards article, as it's more prestigious to have sth published:
    chosen_type = 'article' if 'article' in bibtex_doc_types else bibtex_doc_types[0]
    return chosen_type, FIELDS_FOR_ENTRY_TYPE[chosen_type] + COMMON_FIELDS_FOR_ENTRIES


def get_authors_with_role(authors, role):
    """
    Extract names of people from an authors field given their roles.
    :param authors: Authors field of the record.
    :param role: String specifying the role 'author', 'editor', etc.
    :return: List of names of people.
    """
    return [author['full_name'] for author in authors if role in author.get('inspire_roles', ['author'])]


# Functions below describe where the non-obvious data is located:
# Arguments:
# - data: data partially serialized by the means of defined marshmallow schema only
# - doc_type: *BibTeX* document type, as reported by `bibtex_document_type`

extractor = make_extractor()


@extractor('author')
def get_author(data, doc_type):
    """
    Note: Only used to generate author field if corporate_author is the author.
    """
    if 'corporate_author' in data:
        return ', '.join(data['corporate_author'])


@extractor('journal')
def get_journal(data, doc_type):
    return get_value(data, 'publication_info.journal')


@extractor('volume')
def get_volume(data, doc_type):
    if 'publication_info' in data:
        return data['publication_info'].get('volume')
    return get_value(data, 'book_series.volume')


@extractor('year')
def get_year(data, doc_type):
    publication_year = get_value(data, 'publication_info.year')
    thesis_year = get_value(data, 'thesis_info.date[0]')
    imprint_year = get_value(data, 'imprints.date[0]')

    if doc_type.endswith('thesis'):
        return thesis_year or publication_year or imprint_year
    return publication_year or thesis_year or imprint_year


@extractor('number')
def get_number(data, doc_type):
    return get_value(data, 'publication_info.number')


@extractor('pages')
def get_pages(data, doc_type):
    page_start = get_value(data, 'publication_info.page_start')
    page_end = get_value(data, 'publication_info.page_end')
    return "{}--{}".format(page_start, page_end) if page_start and page_end \
        else get_value(data, 'publication_info.artid')


@extractor('primaryClass')
def get_primary_class(data, doc_type):
    return get_value(data, 'arxiv_eprints.categories[0]')


@extractor('eprint')
def get_eprint(data, doc_type):
    return get_value(data, 'arxiv_eprints.value')


@extractor('archivePrefix')
def get_arxiv_prefix(data, doc_type):
    if get_eprint(data, doc_type):
        return "arXiv"


@extractor('SLACcitation')
def get_slac_citation(data, doc_type):
    eprint = get_value(data, 'arxiv_eprints.value')

    def format_field(reference):
        return "%%CITATION = {};%%".format(reference).upper()

    if 'doi' in data:
        return format_field('doi:' + data['doi'])
    elif eprint:
        slac_prefix = 'ARXIV:' if is_arxiv_post_2007(eprint) else ''
        return format_field(slac_prefix + eprint)
    elif 'reportNumber' in data:
        return format_field(data['reportNumber'][0])


@extractor('school')
def get_school(data, doc_type):
    schools = get_value(data, 'thesis_info.institutions')
    if schools:
        return ', '.join(schools)


@extractor('address')
def get_address(data, doc_type):
    pubinfo_address = get_value(data, 'publication_info.conference.address')
    imprint_address = get_value(data, 'imprints.place')
    return pubinfo_address or imprint_address


@extractor('booktitle')
def get_booktitle(data, doc_type):
    return get_value(data, 'publication_info.conference.title') \
        or get_value(data, 'book_series.title')


@extractor('publisher')
def get_publisher(data, doc_type):
    return get_value(data, 'imprints.publisher')


@extractor('reportNumber')
def get_report_number(data, doc_type):
    if 'reportNumber' in data:
        return ', '.join(data['reportNumber'])


@extractor('isbn')
def get_isbn(data, doc_type):
    if 'isbn' in data:
        return ', '.join(data['isbn'])


@extractor('type')
def get_type(data, doc_type):
    if doc_type == 'mastersthesis' and data['thesis_info']['degree_type'] != 'master':
        return "{} thesis".format(data['thesis_info']['degree_type'].title())


@extractor('edition')
def get_edition(data, doc_type):
    return get_value(data, 'editions[0]')
