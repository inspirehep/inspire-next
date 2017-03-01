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

from copy import deepcopy
from uuid import uuid4

from sqlalchemy import desc

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.disambiguation.models import DisambiguationRecord
from inspirehep.modules.disambiguation.receivers import (
    append_new_record_to_queue,
    append_updated_record_to_queue,
)
from inspirehep.modules.records.api import InspireRecord


class _IdDict(dict):

    def __init__(self, *args, **kwargs):
        super(_IdDict, self).__init__(*args, **kwargs)
        self._id = uuid4()

    @property
    def id(self):
        return self._id


def test_append_new_record_to_queue_method(small_app):
    """Test the receiver responsible for queuing new HEP records."""
    sample_hep_record = _IdDict({
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'authors': [{
            'affiliations': [{'value': 'Copenhagen U.'}],
            'curated_relation': False,
            'full_name': 'Glashow, S.L.',
            'signature_block': 'GLASs',
            'uuid': '5ece3c81-0a50-481d-8bee-5f78576e9504'
        }],
        'control_number': 4328,
        'self': {'$ref': 'http://localhost:5000/api/literature/4328'},
        'titles': [{'title': 'Partial Symmetries of Weak Interactions'}]
    })

    append_new_record_to_queue(sample_hep_record)

    assert str(sample_hep_record.id) == \
        DisambiguationRecord.query.order_by(desc('id')).first().record_id


def test_append_new_record_to_queue_method_not_hep_record(small_app):
    """Test if the receiver will skip a new publication, not HEP."""
    sample_author_record = _IdDict({
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        '_collections': ['Authors'],
        'control_number': 314159265,
        'name': {'value': 'Glashow, S.L.'},
        'positions': [{'institution': {'name': 'Copenhagen U.'}}],
        'self': {'$ref': 'http://localhost:5000/api/authors/314159265'}})

    append_new_record_to_queue(sample_author_record)

    assert str(sample_author_record.id) != \
        DisambiguationRecord.query.order_by(desc('id')).first().record_id


def test_append_updated_record_to_queue(small_app):
    """Test the receiver responsible for queuing updated HEP records."""
    pid = PersistentIdentifier.get('lit', 4328)
    publication_id = str(pid.object_uuid)
    record = InspireRecord.get_record(publication_id)

    record_to_update = deepcopy(record)
    record_to_update['authors'][0]['full_name'] = 'John Smith'

    append_updated_record_to_queue(None, record_to_update, record_to_update,
                                   'records-hep', 'hep')

    assert str(record_to_update.id) == \
        DisambiguationRecord.query.order_by(desc('id')).first().record_id


def test_append_updated_record_to_queue_new_record(small_app):
    """Test if the receiver will return None, since the record will
    not be found in the Elasticsearch instance.

    This record will be caught by 'append_new_record_to_queue' signal.
    """
    sample_hep_record = _IdDict({
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'authors': [{
            'affiliations': [{'value': 'Copenhagen U.'}],
            'curated_relation': False,
            'full_name': 'Glashow, S.L.',
            'signature_block': 'GLASs',
            'uuid': '5ece3c81-0a50-481d-8bee-5f78576e9504'
        }],
        'control_number': 4328,
        'self': {'$ref': 'http://localhost:5000/api/literature/4328'},
        'titles': [{'title': 'Partial Symmetries of Weak Interactions'}]
    })

    result = append_updated_record_to_queue(None, sample_hep_record,
                                            sample_hep_record, 'records-hep',
                                            'hep')

    assert result is None
    assert str(sample_hep_record.id) != \
        DisambiguationRecord.query.order_by(desc('id')).first().record_id


def test_append_updated_record_to_queue_not_hep_record(small_app):
    """Test if the receiver will skip an updated publication, not HEP."""
    sample_author_record = _IdDict({
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        '_collections': ['Authors'],
        'control_number': 314159265,
        'name': {'value': 'Glashow, S.L.'},
        'positions': [{'institution': {'name': 'Copenhagen U.'}}],
        'self': {'$ref': 'http://localhost:5000/api/authors/314159265'}})

    append_updated_record_to_queue(None, sample_author_record,
                                   sample_author_record, 'records-authors',
                                   'authors')

    assert str(sample_author_record.id) != \
        DisambiguationRecord.query.order_by(desc('id')).first().record_id


def test_append_updated_record_to_queue_same_data(small_app):
    """Check if for the same record, the receiver will skip the publication."""
    pid = PersistentIdentifier.get('lit', 11883)
    publication_id = str(pid.object_uuid)
    record = InspireRecord.get_record(publication_id)

    append_updated_record_to_queue(None, record, record, 'records-hep', 'hep')

    assert str(record.id) != \
        DisambiguationRecord.query.order_by(desc('id')).first().record_id
