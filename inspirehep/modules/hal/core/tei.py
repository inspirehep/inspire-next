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

"""HAL TEI Core."""

from __future__ import absolute_import, division, print_function

from elasticsearch import RequestError
from flask import current_app, render_template
from nameparser import HumanName

from inspirehep.dojson.utils import get_recid_from_ref
from inspirehep.modules.records.json_ref_loader import replace_refs
from inspirehep.utils.dedupers import dedupe_list_of_dicts
from inspirehep.utils.record import get_value
from inspirehep.utils.record_getter import get_es_records


def convert_to_tei(record):
    """Returns the record formatted in XML+TEI per HAL's specification."""
    context = {
        'authors': parse_authors(record),
        'doi': get_first_doi(record),
        'domains': [],  # TODO: implement (see #1590).
        'publication': parse_publication_info(record),
        'reviewed': is_peer_reviewed(record),
        'structures': parse_structures(record),
        'titles': get_titles(record),
        'typology': get_typology(record),
    }

    return render_template(current_app.config['HAL_TEI_TEMPLATE'], **context)


def get_first_doi(record):
    return get_value(record, 'dois[0].value', default='')


def get_titles(record):
    return get_value(record, 'titles', default=[])


def get_typology(record):
    mapping = current_app.config['HAL_TYPOLOGY_MAPPING']
    fallback = current_app.config['HAL_TYPOLOGY_FALLBACK']
    document_type = get_value(record, 'document_type[0]')

    return mapping.get(document_type, fallback)


def is_peer_reviewed(record):
    return 'refereed' in record and record['refereed']


def parse_authors(record):
    authors = get_value(record, 'authors', default=[])

    for author in authors:
        try:
            author['parsed_name'] = HumanName(author['full_name']).as_dict()
        except KeyError:
            continue

    return authors


def parse_publication_info(record):
    publication_info = get_value(record, 'publication_info[0]')
    if publication_info:
        if 'journal_title' in publication_info:
            return _parse_journal_publication_info(publication_info)
        elif 'conference_record' in publication_info:
            return _parse_proceedings_publication_info(publication_info)

    return {}


def _parse_journal_publication_info(publication_info):
    def _get_pp(pub_info):
        if 'artid' in pub_info:
            return pub_info['artid']
        elif 'page_start' in pub_info and 'page_end' in pub_info:
            return '{}-{}'.format(pub_info['page_start'], pub_info['page_end'])
        elif 'page_start' in pub_info or 'page_end' in pub_info:
            return pub_info['page_start'] or pub_info['page_end']

        return ''

    return {
        'issue': publication_info.get('journal_issue'),
        'name': publication_info.get('journal_title'),
        'pp': _get_pp(publication_info),
        'type': 'journal',
        'volume': publication_info.get('journal_volume'),
        'year': publication_info.get('year'),
    }


def _parse_proceedings_publication_info(publication_info):
    record = replace_refs(publication_info['conference_record'])

    return {
        'acronym': get_value(record, 'institution_acronym[0]', ''),
        'closing_date': get_value(record, 'closing_date', ''),
        'name': get_value(record, 'titles[0].title', ''),
        'opening_date': get_value(record, 'opening_date', ''),
        'type': 'conference',
    }


def parse_structures(record):
    aff_recids = []

    for author in record.get('authors', []):
        for affiliation in author.get('affiliations', []):
            if affiliation.get('record'):
                recid = get_recid_from_ref(affiliation['record'])

                affiliation['recid'] = recid
                aff_recids.append(str(recid))

    try:
        records = get_es_records('ins', aff_recids)
    except RequestError:
        records = []

    structures = dedupe_list_of_dicts([_parse_structure(el) for el in records])
    structures_not_in_hal = [el for el in structures if not el['hal_id']]

    recid_to_hal_id_map = {
        el['recid']: el['hal_id'] for el in structures if el['hal_id']}

    for author in record.get('authors', []):
        for affiliation in author.get('affiliations', []):
            if affiliation.get('recid') in recid_to_hal_id_map:
                affiliation['hal_id'] = recid_to_hal_id_map[affiliation['recid']]

    return structures_not_in_hal


def _parse_structure(record):
    def _get_hal_id(record):
        def _is_hal_id(id_):
            return id_['type'] == 'HAL'

        ids = get_value(record, 'ids', default=[])
        hal_ids = filter(_is_hal_id, ids)

        return hal_ids[0]['value'] if hal_ids else ''

    return {
        'address': get_value(record, 'address[0].original_address', default=[]),
        'country': get_value(record, 'address[0].country_code', default=''),
        'hal_id': _get_hal_id(record),
        'name': get_value(record, 'institution[0]', default=''),
        'recid': record['control_number'],
        'type': 'institution',
        # ^^ FIXME: Needs to choose from the HAL accepted values:
        # institution, department, laboratory or researchteam
    }
