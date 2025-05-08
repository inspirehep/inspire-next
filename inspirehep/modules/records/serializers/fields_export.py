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

import re

from babel import Locale
from isbnlib import ISBNLibException
from six import text_type

from idutils import is_arxiv_post_2007, normalize_isbn

from inspire_schemas.readers import LiteratureReader
from inspire_utils.date import PartialDate
from inspire_utils.record import get_value

from inspirehep.utils.record_getter import get_conference_record
from .config import COMMON_FIELDS_FOR_ENTRIES, FIELDS_FOR_ENTRY_TYPE


def make_extractor():
    """Create a function store decorator.

    Creates a decorator function that is used to collect extractor functions.
    They are put in a dictionary with the field they extract as keys.
    An extractor function is a function which returns a BibTeX field value given
    an inspire record and a document type.

    Returns:
        function: a decorator with a store for pre-processing/extracting functions.
    """
    store = {}

    def extractor(field):
        def decorator(decorated_function):
            store[field] = decorated_function
            return decorated_function
        return decorator
    extractor.store = store
    return extractor


def bibtex_document_type(doc_type, obj):
    """Return the BibTeX entry type.

    Maps the INSPIRE ``document_type`` to a BibTeX entry type. Also checks
    ``thesis_info.degree_type`` in case it's a thesis, as it stores the
    information on which kind of thesis we're dealing with.

    Args:
        doc_type (text_type): INSPIRE document type.
        obj (dict): literature record.

    Returns:
        text_type: bibtex document type for the given INSPIRE entry.
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
    elif doc_type == 'thesis' and get_value(obj, 'thesis_info.degree_type') in ('phd', 'habilitation'):
        return 'phdthesis'
    # Other types of theses (other, bachelor, laurea) don't have separate types in bibtex:
    # We will use the type field (see `get_type`) to indicate the type of diploma.
    elif doc_type == 'thesis':
        return 'mastersthesis'
    return 'misc'


def bibtex_type_and_fields(data):
    """Return a BibTeX doc type and fields needed to be included in a BibTeX record.

    Args:
        data (dict): inspire record

    Returns:
         tuple: bibtex document type and fields
    """
    # TODO: Establish a better method with which we choose the bibtex type if there is more that one inspire doc type
    bibtex_doc_types = [bibtex_document_type(doc_type, data) for doc_type in data['document_type']] + ['misc']
    # Preference towards article, as it's more prestigious to have sth published:
    chosen_type = 'article' if 'article' in bibtex_doc_types else bibtex_doc_types[0]
    return chosen_type, FIELDS_FOR_ENTRY_TYPE[chosen_type] + COMMON_FIELDS_FOR_ENTRIES


def get_authors_with_role(authors, role):
    """Extract names of people from an authors field given their roles.

    Args:
        authors: authors field of the record.
        role: string specifying the role 'author', 'editor', etc.

    Returns:
        list of text_type: of names of people
    """
    return [author['full_name'] for author in authors if role in author.get('inspire_roles', ['author'])]


def get_country_name_by_code(code, default=None):
    """Return a country name string from a country code.

    Args:
        code (str): country code in INSPIRE 2 letter format based on ISO 3166-1 alpha-2
        default: value to be returned if no country of a given code exists

    Returns:
        text_type: name of a country, or ``default`` if no such country.
    """
    try:
        return Locale('en').territories[code]
    except KeyError:
        return default


def get_best_publication_info(data):
    """Return the most comprehensive publication_info entry.

    Args:
        data (dict): inspire record

    Returns:
        dict: a publication_info entry or default if not found any
    """
    publication_info = get_value(data, 'publication_info', [])
    only_publications = [entry for entry in publication_info if entry.get('material', 'publication') == 'publication']
    if not only_publications:
        return {}

    return sorted(only_publications, key=len, reverse=True)[0]


def get_date(data, doc_type):
    """Return a publication/thesis/imprint date.

    Args:
      data (dict): INSPIRE literature record to be serialized
      doc_type (text_type): BibTeX document type, as reported by `bibtex_document_type`

    Returns:
        PartialDate: publication date for a record.
    """
    publication_year = get_best_publication_info(data).get('year')
    thesis_date = get_value(data, 'thesis_info.date')
    imprint_date = get_value(data, 'imprints.date[0]')

    if doc_type.endswith('thesis'):
        date_choice = thesis_date or publication_year or imprint_date
    else:
        date_choice = publication_year or thesis_date or imprint_date

    if date_choice:
        return PartialDate.loads(str(date_choice))


# Functions below describe where the non-obvious data is located:
#
# Args:
#   data (dict): JSON literature record to be serialized
#   doc_type (text_type): BibTeX document type, as reported by `bibtex_document_type`

extractor = make_extractor()


@extractor('author')
def get_author(data, doc_type):
    """Get corporate author of a record.

    Note:
        Only used to generate author field if corporate_author is the author.
    """
    if 'corporate_author' in data:
        return ' and '.join('{{{}}}'.format(author) for author in data['corporate_author'])


@extractor('journal')
def get_journal(data, doc_type):
    return get_best_publication_info(data).get('journal_title')


@extractor('volume')
def get_volume(data, doc_type):
    publication_volume = get_best_publication_info(data).get('journal_volume')
    bookseries_volume = get_value(data, 'book_series.volume[0]')
    return publication_volume or bookseries_volume


@extractor('year')
def get_year(data, doc_type):
    date = get_date(data, doc_type)
    if date:
        return date.year


@extractor('month')
def get_month(data, doc_type):
    date = get_date(data, doc_type)
    if date:
        return date.month


@extractor('number')
def get_number(data, doc_type):
    return get_best_publication_info(data).get('journal_issue')


@extractor('pages')
def get_pages(data, doc_type):
    pub_info = get_best_publication_info(data)
    return LiteratureReader.get_page_artid_for_publication_info(pub_info, '--')


@extractor('primaryClass')
def get_primary_class(data, doc_type):
    eprint = get_value(data, 'arxiv_eprints.value[0]')
    if eprint and is_arxiv_post_2007(eprint):
        return get_value(data, 'arxiv_eprints[0].categories[0]')


@extractor('eprint')
def get_eprint(data, doc_type):
    return get_value(data, 'arxiv_eprints.value[0]')


@extractor('archivePrefix')
def get_arxiv_prefix(data, doc_type):
    if get_eprint(data, doc_type):
        return "arXiv"


@extractor('school')
def get_school(data, doc_type):
    schools = [school['name'] for school in get_value(data, 'thesis_info.institutions', [])]
    if schools:
        return ', '.join(schools)


@extractor('address')
def get_address(data, doc_type):
    conference = get_conference_record(data, default={})
    pubinfo_city = get_value(conference, 'addresses[0].cities[0]')
    pubinfo_country_code = get_value(conference, 'addresses[0].country_code')

    if pubinfo_city and pubinfo_country_code:
        return pubinfo_city + ', ' + get_country_name_by_code(pubinfo_country_code, default=pubinfo_country_code)
    return get_value(data, 'imprints[0].place')


@extractor('booktitle')
def get_booktitle(data, doc_type):
    book_series_title = get_value(data, 'book_series.title[0]')
    conference_record = get_conference_record(data, default={})
    return book_series_title or LiteratureReader(conference_record).title


@extractor('publisher')
def get_publisher(data, doc_type):
    return get_value(data, 'imprints.publisher[0]')


@extractor('reportNumber')
def get_report_number(data, doc_type):
    if 'report_numbers' in data:
        return ', '.join(report['value'] for report in data.get('report_numbers', []))


@extractor('isbn')
def get_isbn(data, doc_type):
    def hyphenate_if_possible(no_hyphens):
        try:
            return normalize_isbn(no_hyphens)
        except ISBNLibException:
            return no_hyphens

    isbns = get_value(data, 'isbns.value', [])
    if isbns:
        return ', '.join(hyphenate_if_possible(isbn) for isbn in isbns)


@extractor('type')
def get_type(data, doc_type):
    degree_type = get_value(data, 'thesis_info.degree_type', 'other')
    if doc_type == 'mastersthesis' and degree_type not in ('master', 'diploma'):
        return '{} thesis'.format(degree_type.title())


@extractor('edition')
def get_edition(data, doc_type):
    return get_value(data, 'editions[0]')


@extractor('doi')
def get_doi(data, doc_type):
    return get_value(data, 'dois.value[0]')


@extractor('title')
def get_title(data, doc_type):
    return get_value(data, 'titles.title[0]')


@extractor('url')
def get_url(data, doc_type):
    return get_value(data, 'urls.value[0]')


@extractor('collaboration')
def get_collaboration(data, doc_type):
    return ', '.join(get_value(data, 'collaborations.value', default=[]))


@extractor('series')
def get_series(data, doc_type):
    return get_value(data, 'book_series.title[0]')


@extractor('note')
def get_note(data, doc_type):
    """Write and addendum/errata information to the BibTeX note field.

    Traverse publication_info looking for erratum and addendum in `publication_info.material`
    field and build a string of references to those publication entries.

    Returns:
        string: formatted list of the errata and addenda available for a given record

    """
    notices = ('erratum', 'addendum')
    entries = [entry for entry in get_value(data, 'publication_info', []) if entry.get('material') in notices]

    if not entries:
        return None

    note_strings = [
        text_type('{field}: {journal} {volume}, {pages} {year}').format(
            field=entry['material'].title(),
            journal=entry.get('journal_title'),
            volume=entry.get('journal_volume'),
            pages=LiteratureReader.get_page_artid_for_publication_info(entry, '--'),
            year='({})'.format(entry['year']) if 'year' in entry else ''
        ).strip()
        for entry in entries
    ]

    note_string = '[' + ', '.join(note_strings) + ']'
    note_string = re.sub(' +', ' ', note_string)  # Remove possible multiple spaces
    return re.sub(',,', ',', note_string)         # ... and commas
