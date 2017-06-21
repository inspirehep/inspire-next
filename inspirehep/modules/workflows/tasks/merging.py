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

"""Tasks related to record merging."""

from __future__ import absolute_import, division, print_function

import json
from pprint import pformat

from invenio_db import db
from invenio_pidstore.resolver import PersistentIdentifier
from inspire_json_merger.inspire_json_merger import inspire_json_merge

from inspirehep.modules.records import RecordMetadata
from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.records import InspireRecord
from inspirehep.modules.workflows.utils import (
    with_debug_logging,
    store_root_json
)
from inspirehep.utils.record import get_source

from ..errors import MissingHeadUUIDError
from ..utils import (
    with_debug_logging,
    retrieve_root_json,
)


def get_root(obj):
    """Retrieve the root JSON.

    Retrieves the root JSON corresponding to the current matched record and the
    provided source.
    The root version is stored in `obj.extra_data['root_json']`.
    """
    source = get_source(obj.data)
    control_number = obj.data.get('control_number', '')
    record_uuid = PersistentIdentifier.get('lit', control_number).object_uuid
    return retrieve_root_json(record_uuid, source)


def put_head_uuid_in_extra_data(obj):
    """Retrieve the UUID from the JSON record.

    Retrieves the record UUID .
    The uuid is stored in `obj.extra_data['head_uuid']`.
    """
    try:
        rec_id = obj.extra_data['record_matches']['records'][0]['source']['control_number']
    except Exception as e:
        raise ValueError(
            'Can not get control number from matched record.\n{}'
                .format(e.message)
        )
    record_uuid = PersistentIdentifier.get('lit', rec_id).object_uuid
    obj.extra_data['head_uuid'] = str(record_uuid)


def get_head(obj):
    """Retrieve the head from the JSON record.

    Retrieves the head JSON corresponding to the current matched record.
    The head version is stored in `obj.extra_data['head_json']`.
    It assumes that inside obj.extra_data there is head_uuid key populated
    """
    head_uuid = obj.extra_data.get('head_uuid')
    if not head_uuid:
        raise MissingHeadUUIDError

    entry = RecordMetadata.query.filter(
        RecordMetadata.id == head_uuid
    ).one_or_none()

    return entry.json if entry else {}


@with_debug_logging
def merge_articles(obj, eng):
    """Retrieve root, head, update and perform the merge.

    - The workflow payload is overwritten by the merged record.

    - The conflicts are stored in obj.extra_data['conflicts']. This variable
        contains None if there aren't conflicts, otherwise a string made by
        dumping a dictionary.
    """
    root = get_root(obj)
    put_head_uuid_in_extra_data(obj)
    head = get_head(obj)

    obj.data, conflicts = inspire_json_merge(
        root,
        head,
        obj.extra_data['new_root']
    )
    obj.extra_data['conflicts'] = conflicts if conflicts else None


def put_root_in_extradata(obj, eng):
    """Save the workflow object payload in extra_data['new_root']
    to make it available later.
    """
    if not obj.extra_data.get('new_root'):
        obj.extra_data['new_root'] = obj.data


def update_record(obj, eng):
    """Stores the merged record in the database.

    When this function is called, it assumes:
    - obj.extra_data['head_uuid'] is populated
    - obj.data is populated with the json merged
    """
    record = InspireRecord.get_record(obj.extra_data['head_uuid'])
    record.clear()
    record.update(obj.data)
    record.commit()
    obj.save()
    db.session.commit()


@with_debug_logging
def store_root(obj, eng):
    """Stores the root record in the database.

    When this function is called, it assumes:
    - obj.extra_data['head_uuid'] is populated
    - obj.data is populated with the json merged
    """
    new_root = obj.extra_data['new_root']
    store_root_json(
        obj.extra_data['head_uuid'],
        get_source(new_root),
        new_root
    )
    # this line prevent emptying obj.extra_data
    obj.save()
    # Commit to DB before indexing
    db.session.commit()


@with_debug_logging
def store_record(obj, *args, **kwargs):
    """Create and index new record in main record space."""
    obj.log.debug('Storing record: \n%s', pformat(obj.data))

    assert "$schema" in obj.data, "No $schema attribute found!"

    record = InspireRecord.create(obj.data, id_=None)

    # Create persistent identifier.
    inspire_recid_minter(str(record.id), record)

    # store head_uuid to store the root later
    obj.extra_data['head_uuid'] = str(record.id)

    # Commit any changes to record
    record.commit()
    # Dump any changes to record
    obj.data = record.dumps()

    obj.save()
    # Commit to DB before indexing
    db.session.commit()
