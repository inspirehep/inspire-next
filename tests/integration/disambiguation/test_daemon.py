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

import pytest
from mock import patch

from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es

from inspirehep.modules.disambiguation.models import DisambiguationRecord
from inspirehep.utils.record_getter import get_es_record_by_uuid


@pytest.mark.xfail(reason='receivers were detached from signals')
def test_count_phonetic_block_dispatched(small_app):
    """Count if two phonetic blocks were dispatched."""
    from inspirehep.modules.disambiguation.tasks import disambiguation_daemon

    # Check if the queue has three records.
    assert DisambiguationRecord.query.count() == 3

    # Signature #1.
    glashow_record_id = str(PersistentIdentifier.get(
        "literature", 4328).object_uuid)
    glashow_record = get_es_record_by_uuid(glashow_record_id)

    # Add phonetic block to the record.
    glashow_record['authors'][0]['signature_block'] = "GLASs"
    es.index(index='records-hep', doc_type='hep',
             id=glashow_record_id, body=glashow_record)
    es.indices.refresh('records-hep')

    # Signature #2.
    higgs_record_id_first = str(PersistentIdentifier.get(
        "literature", 1358492).object_uuid)
    higgs_record_first = get_es_record_by_uuid(higgs_record_id_first)

    # Add phonetic block to the record.
    higgs_record_first['authors'][0]['signature_block'] = "HAGp"
    es.index(index='records-hep', doc_type='hep',
             id=higgs_record_id_first, body=higgs_record_first)
    es.indices.refresh('records-hep')

    # Signature #3.
    higgs_record_id_second = str(PersistentIdentifier.get(
        "literature", 11883).object_uuid)
    higgs_record_second = get_es_record_by_uuid(higgs_record_id_second)

    # Add phonetic block to the record.
    higgs_record_second['authors'][0]['signature_block'] = "HAGp"
    es.index(index='records-hep', doc_type='hep',
             id=higgs_record_id_second, body=higgs_record_second)
    es.indices.refresh('records-hep')

    with patch("celery.current_app.send_task") as send_to_clustering:
        disambiguation_daemon()

        assert send_to_clustering.call_count == 2


def test_check_if_daemon_has_cleaned_the_queue(small_app):
    """Check if the daemon has cleaned up the queue."""
    from inspirehep.modules.disambiguation.tasks import disambiguation_daemon

    disambiguation_daemon()

    assert DisambiguationRecord.query.count() == 0
