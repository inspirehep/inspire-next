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

from __future__ import absolute_import, division, print_function

import copy
import json
import os
import pkg_resources
import random
import uuid

from inspirehep.modules.records.api import InspireRecord
from invenio_records.models import RecordMetadata
from invenio_search import current_search_client as es

from .base import TestBaseModel, generate_random_string
from .invenio_pidstore import TestPersistentIdentifier


USED_RECIDS = {}
MAX_ES_INT = 2147483647
MAX_RANDOMIZE_TRIES = 100


def get_next_free_recid():
    next_recid_candidate = random.randint(1, MAX_ES_INT)
    cur_try = 0
    while next_recid_candidate in USED_RECIDS and cur_try < MAX_RANDOMIZE_TRIES:
        next_recid_candidate = random.randint(1, MAX_ES_INT)
        cur_try += 1

    if cur_try >= MAX_RANDOMIZE_TRIES:
        raise Exception(
            'Unable to find a non-used record id, tried %d times.' % cur_try
        )

    reserve_recid(next_recid_candidate)
    return next_recid_candidate


def reserve_recid(recid):
    USED_RECIDS[recid] = True


def cleanup():
    global USED_RECIDS
    USED_RECIDS = {}


class TestRecordMetadata(TestBaseModel):
    """Create Record instance.

    Example:
        >>> from factories.db.invenio_records import TestRecordMetadata
        >>> factory = TestRecordMetadata.create_from_kwargs(json={'name': 'joe'})
        >>> factory.record_metadata
        <RecordMetadata (transient 4661300240)>
        >>> factory.record_metadata.json
        {'name': 'joe', '_collections': ['Literature'], 'control_number': 5, 'titles': [{'title': 'dfjMz4eAgcJS1642UvCGPSieqhnIU6DuasOBHVlHA88tGqwpHOv8Kln63wkZ'}], '$schema': 'http://localhost:5000/schemas/record/hep.json', 'document_type': ['article']}
        >>> type(factory.inspire_record)
        <class 'inspirehep.modules.records.api.InspireRecord'>
    """
    model_class = RecordMetadata

    JSON_SKELETON = {
        '$schema': 'http://localhost:5000/schemas/record/hep.json',
        'document_type': ['article'],
        '_collections': ['Literature'],
    }

    @classmethod
    def create_from_kwargs(cls, index_name='', disable_persistent_identifier=False, **kwargs):
        instance = cls()

        updated_kwargs = copy.deepcopy(kwargs)
        if not kwargs.pop('id', None):
            updated_kwargs['id'] = uuid.uuid4()

        json_ = copy.deepcopy(cls.JSON_SKELETON)
        json_.update(kwargs.pop('json', {}))

        if kwargs.get('pid_type', 'lit') == 'lit' and 'titles' not in json_:
            json_.update({
                'titles': [
                    {
                        'title': generate_random_string(60)
                    }
                ]
            })
        if 'control_number' not in json_:
            json_['control_number'] = get_next_free_recid()
        else:
            reserve_recid(json_['control_number'])

        updated_kwargs['json'] = json_

        instance.record_metadata = super(TestRecordMetadata, cls)\
                .create_from_kwargs(updated_kwargs)

        if index_name:
            instance.es_index_result = es.index(
                index=index_name,
                doc_type=index_name.split('-')[-1],
                body=instance.record_metadata.json,
                id=str(instance.record_metadata.id),
                params={}
            )
            instance.es_refresh_result = es.indices.refresh(index_name)
        if not disable_persistent_identifier:
            instance.persistent_identifier = TestPersistentIdentifier\
                    .create_from_kwargs(
                        object_uuid=instance.record_metadata.id,
                        pid_value=instance.record_metadata.json.get('control_number'),
                        **kwargs).persistent_identifier

        instance.inspire_record = InspireRecord(instance.record_metadata.json,
                                                model=RecordMetadata)

        return instance

    @classmethod
    def create_from_file(cls, module_name, filename, **kwargs):
        """Create Record instance from file.

        Note:
            It will look inside the ``fixtures`` directory for the given module.

        Example:
            >>> from factories.db.invenio_records import TestRecordMetadata
            >>> factory = TestRecordMetadata.create_from_file(__name__, filename)
            >>> factory.record_metadata
            <RecordMetadata (transient 4661300240)>
            >>> factory.record_metadata.json
        """
        path = pkg_resources.resource_filename(
            module_name, os.path.join('fixtures', filename))

        data = json.load(open(path))
        return cls.create_from_kwargs(json=data, **kwargs)
