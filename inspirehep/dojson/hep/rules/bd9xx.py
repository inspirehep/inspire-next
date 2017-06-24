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

"""DoJSON rules for MARC fields in 9xx."""

from __future__ import absolute_import, division, print_function

import re
from functools import partial

from dojson import utils

from inspirehep.modules.references.processors import ReferenceBuilder
from inspirehep.utils.helpers import force_list, maybe_int
from inspirehep.utils.pubnote import build_pubnote
from inspirehep.utils.record import get_value

from ..model import hep, hep2marc
from ...utils import force_single_element, get_recid_from_ref, get_record_ref


RE_VALID_PUBNOTE = re.compile(".*,.*,.*(,.*)?")


@hep.over('record_affiliations', '^902..')
@utils.for_each_value
def record_affiliations(self, key, value):
    record = get_record_ref(value.get('z'), 'institutions')

    return {
        'curated_relation': record is not None,
        'record': record,
        'value': value.get('a'),
    }


@hep2marc.over('902', '^record_affiliations$')
@utils.for_each_value
def record_affiliations2marc(self, key, value):
    return {'a': value.get('value')}


@hep.over('document_type', '^980..')
def document_type(self, key, value):
    publication_types = [
        'introductory',
        'lectures',
        'review',
    ]

    special_collections = [
        # XXX: BABAR-AnalysisDocument is treated as a special case below.
        'babar-internal-bais',
        'babar-internal-note',
        'cdf-internal-note',
        'cdf-note',
        'cdshidden',
        'd0-internal-note',
        'd0-preliminary-note',
        'h1-internal-note',
        'h1-preliminary-note',
        'halhidden',
        'hephidden',
        'hermes-internal-note',
        'larsoft-internal-note',
        'larsoft-note',
        'zeus-internal-note',
        'zeus-preliminary-note',
    ]

    document_types = [
        'book',
        'note',
        'report',
        'proceedings',
        'thesis',
    ]

    document_type = self.get('document_type', [])
    publication_type = self.get('publication_type', [])

    a_values = force_list(value.get('a'))
    for a_value in a_values:
        normalized_a_value = a_value.strip().lower()

        if normalized_a_value == 'arxiv':
            continue  # XXX: ignored.
        elif normalized_a_value == 'citeable':
            self['citeable'] = True
        elif normalized_a_value == 'core':
            self['core'] = True
        elif normalized_a_value == 'noncore':
            self['core'] = False
        elif normalized_a_value == 'published':
            self['refereed'] = True
        elif normalized_a_value == 'withdrawn':
            self['withdrawn'] = True
        elif normalized_a_value in publication_types:
            publication_type.append(normalized_a_value)
        elif normalized_a_value == 'babar-analysisdocument':
            self.setdefault('special_collections', []).append('BABAR-ANALYSIS-DOCUMENT')
        elif normalized_a_value in special_collections:
            self.setdefault('special_collections', []).append(normalized_a_value.upper())
        elif normalized_a_value == 'activityreport':
            document_type.append('activity report')
        elif normalized_a_value == 'bookchapter':
            document_type.append('book chapter')
        elif normalized_a_value == 'conferencepaper':
            document_type.append('conference paper')
        elif normalized_a_value in document_types:
            document_type.append(normalized_a_value)

    c_value = force_single_element(value.get('c', ''))
    normalized_c_value = c_value.strip().lower()

    if normalized_c_value == 'deleted':
        self['deleted'] = True

    self['publication_type'] = publication_type
    return document_type


@hep2marc.over('980', '^citeable$')
@utils.for_each_value
def citeable2marc(self, key, value):
    if value:
        return {'a': 'Citeable'}


@hep2marc.over('980', '^core$')
@utils.for_each_value
def core2marc(self, key, value):
    if value:
        return {'a': 'CORE'}

    return {'a': 'NONCORE'}


@hep2marc.over('980', '^deleted$')
@utils.for_each_value
def deleted2marc(self, key, value):
    if value:
        return {'c': 'DELETED'}


@hep2marc.over('980', '^refereed$')
@utils.for_each_value
def referred2marc(self, key, value):
    if value:
        return {'a': 'Published'}


@hep2marc.over('980', '^withdrawn$')
@utils.for_each_value
def withdrawn2marc(self, key, value):
    if value:
        return {'a': 'Withdrawn'}


@hep2marc.over('980', '^publication_type$')
@utils.for_each_value
def publication_type2marc(self, key, value):
    return {'a': value}


@hep2marc.over('980', '^special_collections$')
@utils.for_each_value
def special_collections2marc(self, key, value):
    if value == 'BABAR-ANALYSIS-DOCUMENT':
        return {'a': 'BABAR-AnalysisDocument'}

    return {'a': value}


@hep2marc.over('980', '^document_type$')
@utils.for_each_value
def document_type2marc(self, key, value):
    if value == 'article':
        return

    return {'a': value.title().replace(' ', '')}


@hep.over('references', '^999C5')
@utils.for_each_value
def references(self, key, value):
    def _get_reference(value):
        def _set_record(el):
            recid = maybe_int(el)
            record = get_record_ref(recid, 'literature')
            rb.set_record(record)

        rb = ReferenceBuilder()
        mapping = [
            ('0', _set_record),
            ('a', rb.add_uid),
            ('b', rb.add_uid),
            ('c', rb.add_collaboration),
            ('e', partial(rb.add_author, role='ed.')),
            ('h', rb.add_refextract_authors_str),
            ('i', rb.add_uid),
            ('k', rb.set_texkey),
            ('m', rb.add_misc),
            ('o', rb.set_label),
            ('p', rb.set_publisher),
            ('q', rb.add_parent_title),
            ('r', rb.add_report_number),
            ('s', rb.set_pubnote),
            ('t', rb.add_title),
            ('u', rb.add_url),
            ('x', rb.add_raw_reference),
            ('y', rb.set_year),
        ]

        for field, method in mapping:
            for el in force_list(value.get(field)):
                if el:
                    method(el)

        return rb.obj

    return _get_reference(value)


@hep2marc.over('999C5', '^references$')
@utils.for_each_value
def references2marc(self, key, value):
    reference = value['reference']

    pids = force_list(reference.get('persistent_identifiers'))
    a_values = ['doi:' + el for el in force_list(reference.get('dois'))]
    a_values.extend(['hdl:' + el['value'] for el in pids if el.get('schema') == 'HDL'])
    a_values.extend(['urn:' + el['value'] for el in pids if el.get('schema') == 'URN'])

    authors = force_list(reference.get('authors'))
    e_values = [el['full_name'] for el in authors if el.get('inspire_role') == 'editor']
    h_values = [el['full_name'] for el in authors if el.get('inspire_role') != 'editor']

    r_values = force_list(reference.get('report_number'))
    r_values.extend(['arXiv:' + el for el in force_list(reference.get('arxiv_eprint'))])

    journal_title = get_value(reference, 'publication_info.journal_title')
    journal_volume = get_value(reference, 'publication_info.journal_volume')
    page_start = get_value(reference, 'publication_info.page_start')
    page_end = get_value(reference, 'publication_info.page_end')
    artid = get_value(reference, 'publication_info.artid')
    s_value = build_pubnote(journal_title, journal_volume, page_start, page_end, artid)

    return {
        '0': get_recid_from_ref(value.get('record')),
        'a': a_values,
        'b': get_value(reference, 'publication_info.cnum'),
        'c': reference.get('collaborations'),
        'e': e_values,
        'h': h_values,
        'i': reference.get('isbn'),
        'k': reference.get('texkey'),
        'm': reference.get('misc'),
        'o': reference.get('label'),
        'p': get_value(reference, 'imprint.publisher'),
        'q': get_value(reference, 'publication_info.parent_title'),
        'r': r_values,
        's': s_value,
        't': get_value(reference, 'title.title'),
        'u': get_value(reference, 'urls.value'),
        'x': get_value(value, 'raw_refs.value'),
        'y': get_value(reference, 'publication_info.year'),
    }
