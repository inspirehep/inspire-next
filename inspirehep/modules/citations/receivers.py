# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Signal receivers for invenio_records."""

from invenio_records.signals import (
    after_record_insert,
    before_record_index,
)

from .tasks import update_citation_count_for_records
from .utils import calculate_citation_count


@after_record_insert.connect
def catch_citations_insert(sender, *args, **kwargs):
    """Trigger update of citation count for all the records affected by insert.

    :param sender: The json representation of the record that is going to be inserted
    """
    records_to_recompute = []
    if 'references' in sender:
        records_to_recompute = [ref['recid'] for ref in sender['references'] if ref.get('recid')]

    if records_to_recompute:
        # countdown added as it takes a while before an indexed record can be accessed from es
        update_citation_count_for_records.apply_async(args=[records_to_recompute], countdown=3)


@before_record_index.connect
def add_citation_count_on_insert_or_update(sender, *args, **kwargs):
    """Add citation_count field on record insert/update."""
    if kwargs is not None:
        json = kwargs.get('json')
        index = kwargs.get('index')
        if json and index == 'hep':
            calculate_citation_count(sender, json)


@before_record_index.connect
def catch_citations_update(recid, json, index, **kwargs):
    """Trigger update of citation count for all the records affected by sender.

    :param sender: The json representation of the record that is going to be updated
    """
    from invenio_ext.es import es
    from elasticsearch.exceptions import NotFoundError
    try:
        current_record = es.get_source(index=index, id=recid, doc_type='record')
    except (ValueError, NotFoundError):
        # Not in ES
        return
    if current_record:
        refs_before_update = [
            ref['recid']
            for ref in current_record.get('references', [])
            if ref.get('recid')
        ]
        refs_after_update = [
            ref['recid']
            for ref in json.get('references', [])
            if ref.get('recid')
        ]
        refs_diff = list(set(refs_before_update) ^ set(refs_after_update))

        if refs_diff:
            # countdown added as it takes a while before an indexed record can be accessed from es
            update_citation_count_for_records.apply_async(args=[refs_diff], countdown=3)
