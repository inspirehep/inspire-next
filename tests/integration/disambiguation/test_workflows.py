# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from inspirehep.modules.records.api import InspireRecord
from inspirehep.utils.record_getter import get_es_record_by_uuid


class _BeardObject(tuple):

    def get(self):
        return self


class _ConflictObject(dict):

    def get(self):
        return self


@pytest.mark.xfail
def test_single_signature_with_no_profile(small_app):
    """Check the module for the case with a single, new signature."""
    from inspirehep.modules.disambiguation.tasks import (
        disambiguation_clustering,
        update_authors_recid
    )

    record_id = str(PersistentIdentifier.get('lit', 11883).object_uuid)
    record = get_es_record_by_uuid(record_id)
    author_uuid = record['authors'][0]['uuid']

    # Add phonetic block to the record.
    record['authors'][0]['signature_block'] = "HAGp"
    es.index(index='records-hep', doc_type='hep',
             id=record_id, body=record)
    es.indices.refresh('records-hep')

    with patch("celery.current_app.send_task",
               return_value=_BeardObject(({}, {"0": [author_uuid]}))):
        with patch("inspirehep.modules.disambiguation.tasks.update_authors_recid.delay",
                   side_effect=update_authors_recid):
            disambiguation_clustering("HAGp")

    assert InspireRecord.get_record(record_id)['authors'][0]['recid'] == "1"


@pytest.mark.xfail
def test_match_signature_with_existing_profile(small_app):
    """Check the module for the case with signatures and existing profile."""
    from inspirehep.modules.disambiguation.tasks import (
        disambiguation_clustering,
        update_authors_recid
    )

    old_record_id = str(PersistentIdentifier.get('lit', 11883).object_uuid)
    old_record = get_es_record_by_uuid(old_record_id)
    old_author_uuid = old_record['authors'][0]['uuid']

    # Add phonetic block to the record.
    old_record['authors'][0]['signature_block'] = "HAGp"
    es.index(index='records-hep', doc_type='hep',
             id=old_record_id, body=old_record)
    es.indices.refresh('records-hep')

    record_id = str(PersistentIdentifier.get('lit', 1358492).object_uuid)
    record = get_es_record_by_uuid(record_id)
    author_uuid = record['authors'][0]['uuid']

    # Add phonetic block to the record.
    record['authors'][0]['signature_block'] = "HAGp"
    es.index(index='records-hep', doc_type='hep',
             id=record_id, body=record)
    es.indices.refresh('records-hep')

    with patch("celery.current_app.send_task",
               return_value=_BeardObject(
                   ({"1": [old_author_uuid, author_uuid]}, {}))):
        with patch("inspirehep.modules.disambiguation.tasks.update_authors_recid.delay",
                   side_effect=update_authors_recid):
            disambiguation_clustering("HAGp")

    assert InspireRecord.get_record(old_record_id)['authors'][0]['recid'] == "1"
    assert InspireRecord.get_record(record_id)['authors'][0]['recid'] == "1"


@pytest.mark.xfail
def test_appoint_profile_from_claimed_signature(small_app):
    """Check the module for the case where claimed signature takes
    everything.
    """
    from inspirehep.modules.disambiguation.tasks import (
        disambiguation_clustering,
        update_authors_recid
    )

    old_record_id = str(PersistentIdentifier.get('lit', 11883).object_uuid)
    old_record = get_es_record_by_uuid(old_record_id)
    old_author_uuid = old_record['authors'][0]['uuid']

    # Add phonetic block to the record.
    old_record['authors'][0]['signature_block'] = "HAGp"
    old_record['authors'][0]['recid'] = "2"
    es.index(index='records-hep', doc_type='hep',
             id=old_record_id, body=old_record)
    es.indices.refresh('records-hep')

    record_id = str(PersistentIdentifier.get('lit', 1358492).object_uuid)
    record = get_es_record_by_uuid(record_id)
    author_uuid = record['authors'][0]['uuid']

    # Add phonetic block to the record.
    record['authors'][0]['signature_block'] = "HAGp"
    record['authors'][0]['recid'] = "314159265"
    record['authors'][0]['curated_relation'] = True
    es.index(index='records-hep', doc_type='hep',
             id=record_id, body=record)
    es.indices.refresh('records-hep')

    with patch("celery.current_app.send_task",
               return_value=_BeardObject(
                   ({"2": [old_author_uuid, author_uuid]}, {}))):
        with patch("inspirehep.modules.disambiguation.tasks.update_authors_recid.delay",
                   side_effect=update_authors_recid):
            disambiguation_clustering("HAGp")

    assert InspireRecord.get_record(old_record_id)['authors'][0]['recid'] == \
        "314159265"
    assert InspireRecord.get_record(record_id)['authors'][0]['recid'] == \
        "314159265"

@pytest.mark.xfail
def test_solve_claim_conflicts(small_app):
    """Check the module for the case where at least two claimed
    signatures are assigned to the same cluster.
    """
    from inspirehep.modules.disambiguation.tasks import (
        disambiguation_clustering,
        update_authors_recid
    )

    # Claimed signature #1.
    glashow_record_id_claimed = str(
        PersistentIdentifier.get('lit', 4328).object_uuid)
    glashow_record_claimed = get_es_record_by_uuid(
        glashow_record_id_claimed)
    glashow_record_uuid_claimed = glashow_record_claimed[
        'authors'][0]['uuid']

    # Add phonetic block to the record.
    glashow_record_claimed['authors'][0]['signature_block'] = "HAGp"
    glashow_record_claimed['authors'][0]['curated_relation'] = True
    glashow_record_claimed['authors'][0]['recid'] = "3"
    es.index(index='records-hep', doc_type='hep',
             id=glashow_record_id_claimed, body=glashow_record_claimed)
    es.indices.refresh('records-hep')

    # Claimed signature #2.
    higgs_record_id_claimed = str(
        PersistentIdentifier.get('lit', 1358492).object_uuid)
    higgs_record_claimed = get_es_record_by_uuid(
        higgs_record_id_claimed)
    higgs_record_uuid_claimed = higgs_record_claimed[
        'authors'][0]['uuid']

    # Add phonetic block to the record.
    higgs_record_claimed['authors'][0]['signature_block'] = "HAGp"
    higgs_record_claimed['authors'][0]['curated_relation'] = True
    higgs_record_claimed['authors'][0]['recid'] = "4"
    es.index(index='records-hep', doc_type='hep',
             id=higgs_record_id_claimed, body=higgs_record_claimed)
    es.indices.refresh('records-hep')

    # Not claimed signature.
    higgs_record_id_not_claimed = str(
        PersistentIdentifier.get('lit', 11883).object_uuid)
    higgs_record_not_claimed = get_es_record_by_uuid(
        higgs_record_id_not_claimed)
    higgs_record_uuid_not_claimed = higgs_record_not_claimed[
        'authors'][0]['uuid']

    # Add phonetic block to the record.
    higgs_record_not_claimed['authors'][0]['signature_block'] = "HAGp"
    es.index(index='records-hep', doc_type='hep',
             id=higgs_record_id_not_claimed, body=higgs_record_not_claimed)
    es.indices.refresh('records-hep')

    with patch("celery.current_app.send_task",
               return_value=_BeardObject(
                   ({"3": [glashow_record_uuid_claimed,
                           higgs_record_uuid_claimed,
                           higgs_record_uuid_not_claimed]}, {}))):
        with patch(
            "inspirehep.modules.disambiguation.logic._solve_claims_conflict",
            return_value=_ConflictObject(
                {higgs_record_uuid_claimed: [
                    higgs_record_uuid_not_claimed]})):
            with patch("inspirehep.modules.disambiguation.tasks.update_authors_recid.delay", side_effect=update_authors_recid):
                disambiguation_clustering("HAGp")

    assert InspireRecord.get_record(
        higgs_record_id_not_claimed)['authors'][0]['recid'] == "4"
