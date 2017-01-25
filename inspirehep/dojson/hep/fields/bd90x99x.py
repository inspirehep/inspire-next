# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""MARC 21 model definition."""

from __future__ import absolute_import, division, print_function

import re
from functools import partial

from dojson import utils

from ..model import hep, hep2marc
from ...utils import (
    get_int_value,
    get_recid_from_ref,
    get_record_ref,
)

from inspirehep.modules.references.processors import ReferenceBuilder
from inspirehep.utils.pubnote import build_pubnote
from inspirehep.utils.record import get_value
from inspirehep.utils.helpers import force_force_list


RE_VALID_PUBNOTE = re.compile(".*,.*,.*(,.*)?")


@hep.over('references', '^999C5')
def references(self, key, value):
    """Produce list of references."""
    value = force_force_list(value)

    def get_value(value):
        # Retrieve fields as described here:
        # https://twiki.cern.ch/twiki/bin/view/Inspire/DevelopmentRecordMarkup.
        rb = ReferenceBuilder()
        mapping = [
            ('o', rb.set_number),
            ('m', rb.add_misc),
            ('x', partial(rb.add_raw_reference, source='dojson')),
            ('1', rb.set_texkey),
            ('u', rb.add_url),
            ('r', rb.add_report_number),
            ('s', rb.set_pubnote),
            ('p', rb.set_publisher),
            ('y', rb.set_year),
            ('i', rb.add_uid),
            ('b', rb.add_uid),
            ('a', rb.add_uid),
            ('c', rb.add_collaboration),
            ('q', rb.add_title),
            ('t', rb.add_title),
            ('h', rb.add_refextract_authors_str),
            ('e', partial(rb.add_author, role='ed.'))
        ]

        for field, method in mapping:
            for element in force_force_list(value.get(field)):
                if element:
                    method(element)

        if '0' in value:
            recid = get_int_value(value, '0')
            rb.set_record(get_record_ref(recid, 'literature'))

        return rb.obj

    references = self.get('references', [])
    references.extend(get_value(v) for v in value)
    return references


@hep2marc.over('999C5', 'references')
@utils.for_each_value
def references2marc(self, key, value):
    """Produce list of references."""
    repnos = value['reference'].get('arxiv_eprints', [])
    reference = value['reference']
    # If not found it will be filtered anyway.
    repnos.append(get_value(reference, 'publication_info.parent_report_number'))
    journal_title = get_value(reference, 'publication_info.journal_title')
    journal_volume = get_value(reference, 'publication_info.journal_volume')
    journal_pg_start = get_value(reference, 'publication_info.page_start')
    journal_pg_end = get_value(reference, 'publication_info.page_end')
    journal_artid = get_value(reference, 'publication_info.artid')
    pubnote = build_pubnote(journal_title, journal_volume, journal_pg_start,
                            journal_pg_end, journal_artid)
    return {
        '0': get_recid_from_ref(value.get('record')),
        '1': get_value(reference, 'texkey'),
        'a': get_value(reference, 'dois[0]'),
        'c': get_value(reference, 'collaboration'),
        'e': [a.get('full_name') for a in reference.get('authors', [])
              if a.get('role') == 'ed.'],
        'h': [a.get('full_name') for a in reference.get('authors', [])
              if a.get('role') != 'ed.'],
        'm': get_value(reference, 'misc'),
        'o': get_value(reference, 'number'),
        'i': get_value(reference, 'publication_info.parent_isbn'),
        'p': get_value(reference, 'imprint.publisher'),
        'r': repnos,
        't': get_value(reference, 'titles[:].title'),
        'u': get_value(reference, 'urls[:].value'),
        's': pubnote,
        'x': get_value(value, 'raw_refs[:].value'),
        'y': get_value(reference, 'publication_info.year')
    }
