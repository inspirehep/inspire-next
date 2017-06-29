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

from invenio_pidstore.resolver import PersistentIdentifier

from inspirehep.utils.record import get_source
from inspire_json_merger.inspire_json_merger import inspire_json_merge

from ..errors import MissingHeadUUIDError
from ..utils import (
    with_debug_logging,
    retrieve_root_json,
    retrieve_head_json,
    store_head_json,
    store_root_json,
)


@with_debug_logging
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


@with_debug_logging
def get_uuid_from_matched_record(obj):
    """Retrieve the UUID from the JSON record.

    Retrieves the record UUID .
    The uuid is stored in `obj.extra_data['head_uuid']`.
    """
    recid = obj.extra_data['record_matches']['records'][0]['source']['control_number']
    record_uuid = PersistentIdentifier.get('lit', recid).object_uuid
    obj.extra_data['head_uuid'] = str(record_uuid)


@with_debug_logging
def get_head(obj):
    """Retrieve the head from the JSON record.

    Retrieves the head JSON corresponding to the current matched record.
    The head version is stored in `obj.extra_data['head_json']`.
    It assumes that inside obj.extra_data there is head_uuid key populated
    """
    head_uuid = obj.extra_data.get('head_uuid')
    if not head_uuid:
        raise MissingHeadUUIDError

    return retrieve_head_json(head_uuid)


def merge_articles(obj, eng):
    """ Retrieve root, head, update and perform the merge.

    The workflow object is replaced with the merged object.
    The conflicts are stored in obj.extra_data['conflicts']
    instead the new_root is stored in obj.extra_data['new_root']
    """
    root = get_root(obj)
    get_uuid_from_matched_record(obj)
    head = get_head(obj)

    obj.extra_data['new_root'] = obj.data

    obj.data, obj.extra_data['conflicts'] = inspire_json_merge(
        root,
        head,
        obj.extra_data['new_root']
    )

    obj.extra_data['merged_record'] = True


def store_temporary_root(obj, eng):
    """Savet the root in extra_data to get it later to store it in the database."""
    if not obj.extra_data.get('new_root'):
        obj.extra_data['new_root'] = obj.data


def store_new_head(obj, eng):
    """Stores the merged record in the database.

    When this function is called, it assumes:
    - obj.extra_data['head_uuid'] is populated
    - obj.data is populated with the json merged
    """
    store_head_json(obj.extra_data['head_uuid'], obj.data)


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


def is_record_merged(obj, eng):
    """Returns if the current record has been merged"""
    return obj.extra_data.get('merged_record')


def is_there_any_conflict(obj, eng):
    """Returns if the current record has conflicts"""
    return obj.extra_data.get('conflicts')


def submit_to_the_curator(obj, eng):
    # @TODO has to be implemented
    obj.extra_data['approved'] = True
