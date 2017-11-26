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

"""HAL TEI core."""

from __future__ import absolute_import, division, print_function

from flask import render_template
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from inspirehep.utils.record import get_abstract, get_arxiv_id, get_title

from ..utils import (
    get_authors,
    get_collaborations,
    get_conference_city,
    get_conference_country,
    get_conference_end_date,
    get_conference_record,
    get_conference_start_date,
    get_conference_title,
    get_divulgation,
    get_document_types,
    get_doi,
    get_domains,
    get_inspire_id,
    get_journal_issue,
    get_journal_title,
    get_journal_volume,
    get_keywords,
    get_language,
    get_page_artid,
    get_peer_reviewed,
    get_publication_date,
    is_published,
)


def convert_to_tei(record):
    """Return the record formatted in XML+TEI per HAL's specification.

    Args:
        record(InspireRecord): a record.

    Returns:
        string: the record formatted in XML+TEI.

    Examples:
        >>> record = get_db_record('lit', 1407506)
        >>> convert_to_tei(record)
        <?xml version="1.0" encoding="UTF-8"?>
        ...

    """
    if _is_comm(record):
        ctx = _get_comm_context(record)
        return render_template('hal/comm.xml', **ctx)
    elif _is_art(record):
        ctx = _get_art_context(record)
        return render_template('hal/art.xml', **ctx)

    raise NotImplementedError


def _is_comm(record):
    document_types = get_document_types(record)

    return 'conference paper' in document_types


def _get_comm_context(record):
    abstract = get_abstract(record)
    try:
        abstract_language = detect(abstract)
    except LangDetectException:
        abstract_language = ''

    conference_record = get_conference_record(record)
    conference_city = get_conference_city(conference_record)
    conference_country = get_conference_country(conference_record)
    conference_end_date = get_conference_end_date(conference_record)
    conference_start_date = get_conference_start_date(conference_record)
    conference_title = get_conference_title(conference_record)

    return {
        'abstract': abstract,
        'abstract_language': abstract_language,
        'arxiv_id': get_arxiv_id(record),
        'authors': get_authors(record),
        'collaborations': get_collaborations(record),
        'conference_city': conference_city,
        'conference_country': conference_country,
        'conference_end_date': conference_end_date,
        'conference_start_date': conference_start_date,
        'conference_title': conference_title,
        'divulgation': get_divulgation(record),
        'doi': get_doi(record),
        'domains': get_domains(record),
        'inspire_id': get_inspire_id(record),
        'journal_issue': get_journal_issue(record),
        'journal_title': get_journal_title(record),
        'journal_volume': get_journal_volume(record),
        'keywords': get_keywords(record),
        'language': get_language(record),
        'page_artid': get_page_artid(record),
        'peer_reviewed': get_peer_reviewed(record),
        'publication_date': get_publication_date(record),
        'title': get_title(record),
    }


def _is_art(record):
    document_types = get_document_types(record)
    published = is_published(record)

    return 'article' in document_types and published


def _get_art_context(record):
    abstract = get_abstract(record)
    try:
        abstract_language = detect(abstract)
    except LangDetectException:
        abstract_language = ''

    return {
        'abstract': abstract,
        'abstract_language': abstract_language,
        'arxiv_id': get_arxiv_id(record),
        'authors': get_authors(record),
        'collaborations': get_collaborations(record),
        'divulgation': get_divulgation(record),
        'doi': get_doi(record),
        'domains': get_domains(record),
        'inspire_id': get_inspire_id(record),
        'journal_issue': get_journal_issue(record),
        'journal_title': get_journal_title(record),
        'journal_volume': get_journal_volume(record),
        'keywords': get_keywords(record),
        'language': get_language(record),
        'page_artid': get_page_artid(record),
        'peer_reviewed': get_peer_reviewed(record),
        'publication_date': get_publication_date(record),
        'title': get_title(record),
    }
