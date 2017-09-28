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
import re


MAX_AUTHORS_BEFORE_ET_AL = 10  # According to CSE stylebook

# Fields shared among all bibtex entries:
COMMON_FIELDS_FOR_ENTRIES = ['key', 'SLACcitation', 'archivePrefix', 'doi', 'eprint', 'month', 'note', 'primaryClass',
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
    Returns a bibtex document type for an INSPIRE entry.
    Args:
        doc_type: INSPIRE document type.
        obj: Object preloaded by schema.
    Returns:
        Bibtex document type.
    """
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
    if doc_type in DOCUMENT_TYPE_MAP:
        return DOCUMENT_TYPE_MAP[doc_type]
    # Theses need special treatment, because bibtex differentiates between their types:
    elif doc_type == 'thesis' and obj['thesis_info']['degree_type'] in ('phd', 'habilitation'):
        return 'phdthesis'
    # Other types of theses (other, bachelor, laurea) don't have separate types in bibtex:
    # We will use the type field (see `get_type`) to indicate the type of diploma.
    elif doc_type == 'thesis':
        return 'mastersthesis'
    return 'misc'


def bibtex_type_and_fields(data):
    """
    Args:
        inspire record

    Returns:
         tuple: bibtex document type and fields
    """
    # TODO: Establish a method with which we choose the bibtex type if there is more that one inspire doc type
    bibtex_doc_types = [bibtex_document_type(doc_type, data) for doc_type in data['document_type']] + ['misc']
    # Preference towards article, as it's more prestigious to have sth published:
    chosen_type = 'article' if 'article' in bibtex_doc_types else bibtex_doc_types[0]
    return chosen_type, FIELDS_FOR_ENTRY_TYPE[chosen_type] + COMMON_FIELDS_FOR_ENTRIES


def get_authors_with_role(authors, role):
    """
    Extract names of people from an authors field given their roles.
    Args:
        authors: authors field of the record.
        role: string specifying the role 'author', 'editor', etc.

    Returns:
        list of names of people
    """
    return [author['full_name'] for author in authors if role in author.get('inspire_roles', ['author'])]


def parse_partial_date(date_string):
    """
    Deserializes partial or full dates in ISO-8601, e.g. '2017', '2017-09', '2017-09-12'.
    Args:
        date_string: string representing a date in a partial ISO-8601 format
    Returns:
        a tuple (year, month, day), with year, month, day being either text or None
    """
    regex = re.compile(r"^(\d{4})?(?:-(\d{2}))?(?:-(\d{2}))?.*$")
    match = re.search(regex, date_string)
    return match.groups()


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
    return get_value(data, 'publication_info[0].journal_title')


@extractor('volume')
def get_volume(data, doc_type):
    publication_volume = get_value(data, 'publication_info[0].journal_volume')
    bookseries_volume = get_value(data, 'book_series[0].volume')
    return publication_volume or bookseries_volume


@extractor('year')
def get_year(data, doc_type):
    publication_year = unicode(get_value(data, 'publication_info[0].year'))
    thesis_date = get_value(data, 'thesis_info.date')
    imprint_date = get_value(data, 'imprints[0].date')

    if doc_type.endswith('thesis'):
        date_choice = thesis_date or publication_year or imprint_date
    else:
        date_choice = publication_year or thesis_date or imprint_date

    if date_choice:
        return parse_partial_date(date_choice)[0]


@extractor('number')
def get_number(data, doc_type):
    return get_value(data, 'publication_info[0].journal_issue')


@extractor('pages')
def get_pages(data, doc_type):
    page_start = get_value(data, 'publication_info[0].page_start')
    page_end = get_value(data, 'publication_info[0].page_end')
    return "{}--{}".format(page_start, page_end) if page_start and page_end \
        else get_value(data, 'publication_info[0].artid')


@extractor('primaryClass')
def get_primary_class(data, doc_type):
    return get_value(data, 'arxiv_eprints[0].categories[0]')


@extractor('eprint')
def get_eprint(data, doc_type):
    return get_value(data, 'arxiv_eprints[0].value')


@extractor('archivePrefix')
def get_arxiv_prefix(data, doc_type):
    if get_eprint(data, doc_type):
        return "arXiv"


@extractor('SLACcitation')
def get_slac_citation(data, doc_type):
    def format_field(citation):
        return "%%CITATION = {};%%".format(citation).upper()

    doi = get_value(data, 'dois[0].value')
    eprint = get_value(data, 'arxiv_eprints[0].value')
    report_number = get_value(data, 'report_numbers[0].value')

    if doi:
        return format_field('DOI:' + doi)
    elif eprint:
        return format_field('ARXIV:' + eprint if is_arxiv_post_2007(eprint) else eprint)
    elif report_number:
        return format_field(report_number)


@extractor('school')
def get_school(data, doc_type):
    schools = [school['name'] for school in get_value(data, 'thesis_info.institutions')]
    if schools:
        return ', '.join(schools)


@extractor('address')
def get_address(data, doc_type):
    pubinfo_address = get_value(data, 'publication_info[0].conference_record.address[0].postal_address[0]')
    imprint_address = get_value(data, 'imprints[0].place')
    return pubinfo_address or imprint_address


@extractor('booktitle')
def get_booktitle(data, doc_type):
    return get_value(data, 'publication_info[0].conference_record.titles[0].title') \
        or get_value(data, 'book_series[0].title')


@extractor('publisher')
def get_publisher(data, doc_type):
    return get_value(data, 'imprints[0].publisher')


@extractor('reportNumber')
def get_report_number(data, doc_type):
    if 'report_numbers' in data:
        return ', '.join(report['value'] for report in data.get('report_numbers', []))


@extractor('isbn')
def get_isbn(data, doc_type):
    if 'isbns' in data:
        return ', '.join(isbn['value'] for isbn in data['isbns'])


@extractor('type')
def get_type(data, doc_type):
    if doc_type == 'mastersthesis' and data['thesis_info']['degree_type'] not in ('master', 'diploma'):
        return "{} thesis".format(data['thesis_info']['degree_type'].title())


@extractor('edition')
def get_edition(data, doc_type):
    return get_value(data, 'editions[0]')


@extractor('doi')
def get_doi(data, doc_type):
    return get_value(data, 'dois[0].value')


@extractor('title')
def get_title(data, doc_type):
    return get_value(data, 'titles[0].title')


@extractor('url')
def get_url(data, doc_type):
    return get_value(data, 'urls[0].value')


@extractor('key')
def get_key(data, doc_type):
    return get_value(data, 'self_recid')


@extractor('collaboration')
def get_collaboration(data, doc_type):
    return get_value(data, 'collaborations[0].value')
