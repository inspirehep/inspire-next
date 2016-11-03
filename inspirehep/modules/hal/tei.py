# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from elasticsearch import RequestError
from nameparser import HumanName

from inspirehep.dojson.utils import get_recid_from_ref
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.utils.dedupers import dedupe_list
from inspirehep.utils.record import get_value
from inspirehep.utils.record_getter import get_es_records

from .templates import template


def tei_response(record):
    """Returns the record formatted in XML+TEI per HAL's specification.

    :param record: the record to convert
    :type record: invenio_records.api.Record
    :return: XML+TEI output
    :rtype: str
    """
    authors = _parse_authors(record)
    titles = record.get('titles', [])
    doi = _parse_dois(record)
    publication = _parse_pub_info(record)
    structures = _parse_structures(record)
    reviewed = _is_peer_reviewed(record)
    domains = _get_domains(record)
    typology = _get_typology(record)

    context = {
        'authors': authors,
        'titles': titles,
        'doi': doi,
        'publication': publication,
        'structures': structures,
        'reviewed': reviewed,
        'domains': domains,
        'typology': typology,
    }

    return template.render(**context).encode('utf-8')


def _get_domains(record):
    categories = get_value(record, 'arxiv_eprints[0].categories', [])

    return []


def _get_typology(record):
    collections = [entry['primary'].lower()
                   for entry in record.get('collections', [])]
    inspire_to_hal = {
        'conferencepaper': "COMM",
        # Communication dans un congrès / Conference communication
        'thesis': "THESE",
        # Thèse / Thesis
        'proceedings': "DOUV",
        # Direction d'ouvrage, Proceedings / Directions of work, Proceedings
        'book': "OUV",
        # Ouvrage (y compris édition critique et traduction) /
        # Book (includes scholarly edition and translation)
        'bookchapter': "COUV",
        # Chapitre d'ouvrage / Book chapter
        'review': "NOTE",
        # Note de lecture / Book review
        'published': "ART",
        # Article dans une revue / Journal article
        'lectures': "LECTURE",
        # Cours / Course
    }

    typology = next(
        (inspire_to_hal[c] for c in collections if c in inspire_to_hal),
        "OTHER"  # Fallback: Autre publication / Other publication
    )
    return typology


def _is_peer_reviewed(record):
    return {'primary': 'Published'} in record.get('collections', [])


def _parse_structures(record):
    structures = []
    recids = []

    for author in record.get('authors', []):
        for affiliation in author.get('affiliations', []):
            try:
                recids.append(
                    str(get_recid_from_ref(affiliation['record']))
                )
                affiliation['recid'] = get_recid_from_ref(
                    affiliation['record']
                )
            except KeyError:
                continue

    try:
        records = get_es_records('ins', recids)
    except RequestError:
        records = []

    for record in records:
        structures.append(
            _structure_data(record)
        )
    return dedupe_list(structures)


def _parse_pub_info(record):
    try:
        pub_info = _lookup(record, "publication_info[0]")
        if 'journal_title' in pub_info:
            return _journal_data(pub_info)
        elif 'conference_record' in pub_info:
            return _conference_data(pub_info['conference_record'])
        else:
            return None
    except KeyError:
        return None


def _parse_dois(record):
    return get_value(record, "dois[0].value", "")


def _parse_authors(record):
    authors = get_value(record, "authors", [])
    for author in authors:
        try:
            parsed = HumanName(author['full_name'])
            author['parsed_name'] = parsed
        except KeyError:
            continue
    return authors


def _conference_data(conf):
    ref = replace_refs(conf, 'db')

    # FIXME: Add conference city, country, and country code fields
    if ref:
        return {'type': "conference",
                'name': get_value(ref, "titles[0].title", ""),
                'acronym': get_value(ref, "acronym[0]", ""),
                'opening_date': get_value(ref, "opening_date", ""),
                'closing_date': get_value(ref, "closing_date", "")}
    else:
        return {'type': "conference",
                'name': "",
                'acronym': "",
                'opening_date': "",
                'closing_date': ""}


def _journal_data(pub_info):
    if 'page_artid' in pub_info:
        pp = pub_info['page_artid']
    elif 'page_start' in pub_info and 'page_end' in pub_info:
        pp = pub_info['page_start'] + "-" + pub_info['page_end']
    elif 'page_start' in pub_info or 'page_end' in pub_info:
        pp = pub_info['page_start'] or pub_info['page_end']
    else:
        pp = ""

    return {
        'type': "journal",
        'name': pub_info.get('journal_title', ""),
        'year': pub_info.get('year', ""),
        'volume': pub_info.get('journal_volume', ""),
        'issue': pub_info.get('journal_issue', ""),
        'pp': pp,
    }


def _structure_data(struct):
    return {
        'type': get_value(struct, "collections[1].primary", "").lower(),
        # ^^ FIXME: This may not be one of the HAL accepted values:
        # institution, department, laboratory or researchteam
        'name': get_value(struct, "institution[0]", ""),
        'address': get_value(struct, "address[0].original_address", []),
        'country': get_value(struct, "address[0].country_code", ""),
        'recid': get_recid_from_ref(struct['self']),
    }


def _lookup(record, value):
    """Searches a key in a record.

    Uses `get_value` to lookup a key in a JSON record, and
    raises a `KeyError` if it wasn't found.
    """
    result = get_value(record, value)
    if not result:
        raise KeyError
    return result
