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

"""Receivers to catch new publications and record updates."""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

from invenio_indexer.signals import before_record_index
from invenio_records.signals import after_record_insert

from inspirehep.modules.disambiguation.models import DisambiguationRecord


def _needs_beard_reprocessing(authors_before, authors_after):
    """Check if the update affected authors or affiliation(s).

    The method receives a list of authors of a record before
    and after the update was made. Then it compares full names
    of the authors together with affiliations to decide
    if the record should be processed by Beard.

    The Beard model is trained against full names and affiliations
    If any of these fields were changes, then the HEP paper should
    be processed.

    :param authors_before:
        A list of authors of a particular HEP paper.

        Example:
            authors_before = [{
                u'full_name': u'Mukherjee, Anirbit',
                u'uuid': u'76f5e291-b709-4aa9-ae7c-99f361bae591'
            }]

    :param authors_before:
        A list of authors of a particular HEP paper.

        Example:
            authors_after = [{
                u'full_name': u'Mukherjee, Anirbit',
                u'affiliations': [{'value': 'Perimeter Inst. Theor. Phys.'}],
                u'uuid': u'76f5e291-b709-4aa9-ae7c-99f361bae591'
            }]

    :return:
        Boolean value if the HEP paper should be processed by Beard or not.

        Example:
            True
    """
    if len(authors_before) == len(authors_after):
        for index, author_before in enumerate(authors_before):
            # Not every author has an affiliation.
            before_affiliations = author_before.get(
                'affiliations', [])

            # We don't iterate over authors_after, we take the index.
            after_affiliations = authors_after[index].get(
                'affiliations', [])

            before = (author_before['full_name'], before_affiliations)
            after = (authors_after[index]['full_name'], after_affiliations)

            if before != after:
                return True

        return False
    else:
        return True


@after_record_insert.connect
def append_new_record_to_queue(sender, *args, **kwargs):
    """Append a new record to the queue.

    The method receives a record on after_record_insert signal and
    appends the given record UUID to the queue of records to be
    processed by Beard.
    """
    # FIXME: Use a dedicated method when #1355 will be resolved.
    if "hep.json" in sender['$schema']:
        record_arguments = {'record_id': sender.id}

        beard_record = DisambiguationRecord(**record_arguments)
        beard_record.save()


@before_record_index.connect
def append_updated_record_to_queue(sender, json, record, index, doc_type):
    """Append record after an update to the queue.

    The method receives a record on before_record_index signal and
    decides if the updates made are essential to append the record
    to the queue of records to be processed by Beard.
    """
    # FIXME: Use a dedicated method when #1355 will be resolved.
    if "hep.json" in json['$schema']:
        from invenio_search import current_search_client as es
        from elasticsearch.exceptions import NotFoundError

        try:
            before_json = es.get_source(
                index=index, id=record.id, doc_type=doc_type)
        except (ValueError, NotFoundError):
            # The record in not available in the Elasticsearch instance.
            # This will be caught by append_new_record_to_queue method.
            return

        if _needs_beard_reprocessing(before_json['authors'], json['authors']):
            record_arguments = {'record_id': record.id}

            beard_record = DisambiguationRecord(**record_arguments)
            beard_record.save()
