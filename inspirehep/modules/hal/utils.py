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

"""HAL utils."""

from __future__ import absolute_import, division, print_function

from itertools import chain

from elasticsearch import RequestError
from flask import current_app
from six import text_type

from inspire_dojson.utils import get_recid_from_ref
from inspire_schemas.builders.literature import is_citeable
from inspire_utils.helpers import force_list
from inspire_utils.name import ParsedName
from inspire_utils.record import get_value
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.utils.record_getter import get_es_records


def get_authors(record):
    """Return the authors of a record.

    Queries the Institution records linked from the authors affiliations
    to add, whenever it exists, the HAL identifier of the institution to
    the affiliation.

    Args:
        record(InspireRecord): a record.

    Returns:
        list(dict): the authors of the record.

    Examples:
        >>> record = {
        ...     'authors': [
        ...         'affiliations': [
        ...             {
        ...                 'record': {
        ...                     '$ref': 'http://localhost:5000/api/institutions/902725',
        ...                 }
        ...             },
        ...         ],
        ...     ],
        ... }
        >>> authors = get_authors(record)
        >>> authors[0]['hal_id']
        '300037'

    """
    hal_id_map = _get_hal_id_map(record)

    result = []

    for author in record.get('authors', []):
        affiliations = []

        parsed_name = ParsedName.loads(author['full_name'])
        first_name, last_name = parsed_name.first, parsed_name.last

        for affiliation in author.get('affiliations', []):
            recid = get_recid_from_ref(affiliation.get('record'))
            if recid in hal_id_map and hal_id_map[recid]:
                affiliations.append({'hal_id': hal_id_map[recid]})

        result.append({
            'affiliations': affiliations,
            'first_name': first_name,
            'last_name': last_name,
        })

    return result


def get_collaborations(record):
    """Return the collaborations associated with a record.

    Args:
        record(InspireRecord): a record.

    Returns:
        list(str): the collaborations associated with the record.

    Examples:
        >>> record = {'collaborations': [{'value': 'CMS'}]}
        >>> get_collaborations(record)
        ['CMS']

    """
    return get_value(record, 'collaborations.value', default=[])


def get_conference_city(record):
    """Return the first city of a Conference record.

    Args:
        record(InspireRecord): a Conference record.

    Returns:
        string: the first city of the Conference record.

    Examples:
        >>> record = {'address': [{'cities': ['Tokyo']}]}
        >>> get_conference_city(record)
        'Tokyo'

    """
    return get_value(record, 'address[0].cities[0]', default='')


def get_conference_country(record):
    """Return the first country of a Conference record.

    Args:
        record(InspireRecord): a Conference record.

    Returns:
        string: the first country of the Conference record.

    Examples:
        >>> record = {'address': [{'country_code': 'JP'}]}
        >>> get_conference_country(record)
        'jp'

    """
    return get_value(record, 'address.country_code[0]', default='').lower()


def get_conference_end_date(record):
    """Return the closing date of a conference record.

    Args:
        record(InspireRecord): a Conference record.

    Returns:
        string: the closing date of the Conference record.

    Examples:
        >>> record = {'closing_date': '1999-11-19'}
        >>> get_conference_end_date(record)
        '1999-11-19'

    """
    return record.get('closing_date', '')


def get_conference_record(record, default=None):
    """Return the first Conference record associated with a record.

    Queries the database to fetch the first Conference record referenced
    in the ``publication_info`` of the record.

    Args:
        record(InspireRecord): a record.
        default: value to be returned if no conference record present/found

    Returns:
        InspireRecord: the first Conference record associated with the record.

    Examples:
        >>> record = {
        ...     'publication_info': [
        ...         {
        ...             'conference_record': {
        ...                 '$ref': '/api/conferences/972464',
        ...             },
        ...         },
        ...     ],
        ... }
        >>> conference_record = get_conference_record(record)
        >>> conference_record['control_number']
        972464

    """
    replaced = replace_refs(get_value(record, 'publication_info.conference_record[0]'), 'db')
    if replaced:
        return replaced
    else:
        return default


def get_conference_start_date(record):
    """Return the opening date of a conference record.

    Args:
        record(InspireRecord): a Conference record.

    Returns:
        string: the opening date of the Conference record.

    Examples:
        >>> record = {'opening_date': '1999-11-16'}
        >>> get_conference__start_date(record)
        '1999-11-16'

    """
    return record.get('opening_date', '')


def get_conference_title(record, default=''):
    """Return the first title of a Conference record.

    Args:
        record(InspireRecord): a Conference record.

    Returns:
        string: the first title of the Conference record.

    Examples:
        >>> record = {'titles': [{'title': 'Workshop on Neutrino Physics'}]}
        >>> get_conference_title(record)
        'Workshop on Neutrino Physics'

    """
    return get_value(record, 'titles.title[0]', default=default)


def get_divulgation(record):
    """Return 1 if a record is intended for the general public, 0 otherwise.

    Args:
        record(InspireRecord): a record.

    Returns:
        int: 1 if the record is intended for the general public, 0 otherwise.

    Examples:
        >>> get_divulgation({'publication_type': ['introductory']})
        1

    """
    return 1 if 'introductory' in get_value(record, 'publication_type', []) else 0


def get_document_types(record):
    """Return all document types of a record.

    Args:
        record(InspireRecord): a record.

    Returns:
        list(str): all document types of the record.

    Examples:
        >>> get_document_types({'document_type': ['article']})
        ['article']

    """
    return get_value(record, 'document_type', default=[])


def get_doi(record):
    """Return the first DOI of a record.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the first DOI of the record.

    Examples:
        >>> get_doi({'dois': [{'value': '10.1016/0029-5582(61)90469-2'}]})
        '10.1016/0029-5582(61)90469-2'

    """
    return get_value(record, 'dois.value[0]', default='')


def get_domains(record):
    """Return the HAL domains of a record.

    Uses the mapping in the configuration to convert all INSPIRE categories
    to the corresponding HAL domains.

    Args:
        record(InspireRecord): a record.

    Returns:
        list(str): the HAL domains of the record.

    Examples:
        >>> record = {'inspire_categories': [{'term': 'Experiment-HEP'}]}
        >>> get_domains(record)
        ['phys.hexp']

    """
    terms = get_value(record, 'inspire_categories.term', default=[])
    mapping = current_app.config['HAL_DOMAIN_MAPPING']

    return [mapping[term] for term in terms]


def get_inspire_id(record):
    """Return the INSPIRE id of a record.

    Args:
        record(InspireRecord): a record.

    Returns:
        int: the INSPIRE id of the record.

    Examples:
        >>> get_inspire_id({'control_number': 1507156})
        1507156

    """
    return record['control_number']


def get_journal_issue(record):
    """Return the issue of the journal a record was published into.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the issue of the journal the record was published into.

    Examples:
        >>> record = {
        ...    'publication_info': [
        ...        {'journal_issue': '5'},
        ...    ],
        ... }
        >>> get_journal_issue(record)
        '5'

    """
    return get_value(record, 'publication_info.journal_issue[0]', default='')


def get_journal_title(record):
    """Return the title of the journal a record was published into.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the title of the journal the record was published into.

    Examples:
        >>> record = {
        ...     'publication_info': [
        ...         {'journal_title': 'Phys.Part.Nucl.Lett.'},
        ...     ],
        ... }
        >>> get_journal_title(record)
        'Phys.Part.Nucl.Lett.'

    """
    return get_value(record, 'publication_info.journal_title[0]', default='')


def get_journal_volume(record):
    """Return the volume of the journal a record was published into.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the volume of the journal the record was published into.

    Examples:
        >>> record = {
        ...     'publication_info': [
        ...         {'journal_volume': 'D94'},
        ...     ],
        ... }
        >>> get_journal_volume(record)
        'D94'

    """
    return get_value(record, 'publication_info.journal_volume[0]', default='')


def get_keywords(record):
    """Return the keywords assigned to a record.

    Args:
        record(InspireRecord): a record.

    Returns:
        list(str): the keywords assigned to the record.

    Examples:
        >>> record = {
        ...     'keywords': [
        ...         {
        ...             'schema': 'INSPIRE',
        ...             'value': 'CKM matrix',
        ...         },
        ...     ],
        ... }
        >>> get_keywords(record)
        ['CKM matrix']

    """
    return get_value(record, 'keywords.value', default=[])


def get_language(record):
    """Return the first language of a record.

    If it is not specified in the record we assume that the language
    is English, so we return ``'en'``.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the first language of the record.

    Examples:
        >>> get_language({'languages': ['it']})
        'it'

    """
    languages = get_value(record, 'languages', default=[])
    if not languages:
        return 'en'

    return languages[0]


def get_page_artid_for_publication_info(publication_info, separator):
    """Return the page range or the article id of a publication_info entry.

    Args:
        publication_info(dict): a publication_info field entry of a record
        separator(basestring): optional page range symbol, defaults to a single dash

    Returns:
        string: the page range or the article id of the record.

    Examples:
        >>> publication_info = {'artid': '054021'}
        >>> get_page_artid(publication_info)
        '054021'

    """
    if 'artid' in publication_info:
        artid = publication_info['artid']
        return artid
    elif 'page_start' in publication_info and 'page_end' in publication_info:
        page_start = publication_info['page_start']
        page_end = publication_info['page_end']
        return text_type('{}{}{}').format(page_start, text_type(separator), page_end)

    return ''


def get_page_artid(record, separator='-'):
    """Return the page range or the article id of a record.

    Args:
        record(InspireRecord): a record
        separator(basestring): optional page range symbol, defaults to a single dash

    Returns:
        string: the page range or the article id of the record.

    Examples:
        >>> record = {
        ...     'publication_info': [
        ...         {'artid': '054021'},
        ...     ],
        ... }
        >>> get_page_artid(record)
        '054021'

    """
    publication_info = get_value(record, 'publication_info[0]', default={})
    return get_page_artid_for_publication_info(publication_info, separator)


def get_peer_reviewed(record):
    """Return 1 if a record is peer reviewed, 0 otherwise.

    Args:
        record(InspireRecord): a record.

    Returns:
        int: 1 if the record is peer reviewed, 0 otherwise.

    Examples:
        >>> get_peer_reviewed({'refereed': True})
        1

    """
    return 1 if 'refereed' in record and record['refereed'] else 0


def get_publication_date(record):
    """Return the date in which a record was published.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the date in which the record was published.

    Examples:
        >>> get_publication_date({'publication_info': [{'year': 2017}]})
        '2017'

    """
    return str(get_value(record, 'publication_info.year[0]', default=''))


def is_published(record):
    """Return if a record is published.

    We say that a record is published if it is citeable, which means that
    it has enough information in a ``publication_info``, or if we know its
    DOI and a ``journal_title``, which means it is in press.

    Args:
        record(InspireRecord): a record.

    Returns:
        bool: whether the record is published.

    Examples:
        >>> record = {
        ...     'dois': [
        ...         {'value': '10.1016/0029-5582(61)90469-2'},
        ...     ],
        ...     'publication_info': [
        ...         {'journal_title': 'Nucl.Phys.'},
        ...     ],
        ... }
        >>> is_published(record)
        True

    """
    citeable = 'publication_info' in record and is_citeable(record['publication_info'])
    submitted = 'dois' in record and any(
        'journal_title' in el for el in force_list(record.get('publication_info')))

    return citeable or submitted


def _get_hal_id_map(record):
    affiliation_records = chain.from_iterable(get_value(
        record, 'authors.affiliations.record', default=[]))
    affiliation_recids = [get_recid_from_ref(el) for el in affiliation_records]

    try:
        institutions = get_es_records('ins', affiliation_recids)
    except RequestError:
        institutions = []

    return {el['control_number']: _get_hal_id(el) for el in institutions}


def _get_hal_id(record):
    for el in record.get('external_system_identifiers', []):
        if el.get('schema') == 'HAL':
            return el['value']
