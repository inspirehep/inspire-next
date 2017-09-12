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

from invenio_db import db
from invenio_pidstore.resolver import PersistentIdentifier
from inspire_json_merger.inspire_json_merger import inspire_json_merge

from inspirehep.modules.records import RecordMetadata
from inspirehep.modules.records.api import InspireRecord
from inspirehep.utils.record import get_source

from inspirehep.modules.workflows.models import WorkflowsRecordSources


from inspirehep.modules.workflows.errors import MergingError
from inspirehep.modules.workflows.utils import with_debug_logging


def put_matched_record_uuid_in_extra_data(obj):
    """Save in extra_data the key `head_uuid`, with the UUID of the matched
    record from ElasticSearch.
    """
    match_id = _get_match_recid(obj)
    record_uuid = PersistentIdentifier.get('lit', match_id).object_uuid
    obj.extra_data['head_uuid'] = str(record_uuid)


def get_head(obj):
    """Retrieve the head from the JSON record.

    Retrieves the head JSON corresponding to the current matched record.
    The head version is stored in `obj.extra_data['head_json']`.
    It assumes that inside obj.extra_data there is head_uuid key populated
    """
    head_uuid = obj.extra_data.get('head_uuid')
    if not head_uuid:
        raise MergingError(
            "Cannot find uuid in the workflow. wf_obj.id={}".format(obj.id)
        )

    entry = RecordMetadata.query.filter(
        RecordMetadata.id == head_uuid
    ).one_or_none()

    if not entry:
        raise MergingError(
            'Error while loading the head: uuid={}'.format(head_uuid)
        )
    return entry.json


@with_debug_logging
def merge_articles(obj, eng):
    """Retrieve root, head, update and perform the merge.

    The workflow payload is overwritten by the merged record, while the
    list of conflicts is stored in obj.extra_data['conflicts'].

    Args:
        obj(WokrflowObject): the current workflow object
        obj.extra_data['head_uuid'](str): the uuid of the record matched to load
        obj.extra_data['new_root'](dict): the workflow payload after enhancement
    """
    root = get_root(
        source=get_source(obj.data),
        control_number=_get_match_recid(obj)
    )
    put_matched_record_uuid_in_extra_data(obj)
    head = get_head(obj)

    head_source = get_head_source(obj.extra_data.get('head_uuid'))

    obj.data, conflicts = inspire_json_merge(
        root=root,
        head=head,
        update=obj.extra_data['new_root'],
        head_source=head_source
    )

    obj.extra_data['conflicts'] = [json.loads(c.to_json()) for c in conflicts]
    obj.save()


def put_new_root_in_extra_data(obj, eng):
    """Save the workflow object payload in extra_data['new_root']
    to make it available later.
    """
    obj.extra_data['new_root'] = obj.data


def update_record(obj, eng):
    """Stores the merged record in the database.

    Args:
        obj(WokrflowObject): the current workflow object
        obj.extra_data['head_uuid'](str): the uuid of the record matched to load
    """
    record = InspireRecord.get_record(obj.extra_data['head_uuid'])
    record.clear()
    record.update(obj.data)
    record.commit()
    obj.save()
    db.session.commit()


def get_root(source, uuid=None, control_number=None):
    """Retrieve the root JSON.

    Retrieves the root JSON corresponding to the current matched record and the
    provided source.
    The root version is stored in `obj.extra_data['root_json']`.

    Args:
        source(string): the root record source, e.g. 'arxiv'
        uuid(string): the record uuid
        control_number(string): the record control number

    Return:
        (dict): the json of the entry if it exists, else an empty dict
    """
    if not uuid and not control_number:
        raise MergingError('Cannot load Root without any identifier')
    record_uuid = uuid or PersistentIdentifier.get('lit', control_number).object_uuid
    entry = read_wf_record_source(record_uuid, source)
    return entry.json if entry else {}


def _get_match_recid(obj):
    """Return the first matched record by `inspire-matcher`"""
    return obj.extra_data['record_matches'][0]


@with_debug_logging
def store_root(obj, eng):
    """Stores the root record in the database.

    Args:
        obj(WokrflowObject): the current workflow object
        obj.extra_data['head_uuid'](str): the uuid of the record matched to load
        obj.extra_data['new_root'](dict): the workflow payload after enhancement
    """
    new_root = obj.extra_data['new_root']
    record_uuid = obj.extra_data['head_uuid']
    source = get_source(new_root)

    insert_wf_record_source(new_root, record_uuid, source)

    # this line prevent emptying obj.extra_data
    obj.save()
    db.session.commit()


def read_wf_record_source(record_uuid, source):
    entry = WorkflowsRecordSources.query.filter_by(
        record_id=str(record_uuid),
        source=source.lower()
    ).one_or_none()
    return entry


def insert_wf_record_source(json, record_uuid, source):
    """Stores the given json in the WorkflowRecordSource table in the db.
    This object, in the workflow, is known as ``new_root``.

    Important: does not commit the session, in case some other operation
    needs to be done before it

    Args:
        json(dict): the content of the root
        record_uuid(uuid): the record's uuid to associate with the root
        source(string): the source og the root
    """
    record_source = read_wf_record_source(record_uuid=record_uuid, source=source)
    if record_source is None:
        record_source = WorkflowsRecordSources(
            source=source.lower(),
            json=json,
            record_id=record_uuid
        )
        db.session.add(record_source)
    else:
        record_source.json = json


def has_conflicts(obj, eng):
    return obj.extra_data.get('conflicts')


def get_head_source(head_uuid):
    """Return the right source for the record having uuid=``uuid``.

    Args:
        head_uuid(string): the uuid of the record to get the source

    Return:
        (string):
        * ``publisher`` if there is at least a non arxiv root
        * ``arxiv`` if there are no publisher roots and an arxiv root
        * None if there are no root records
    """
    publisher_root = WorkflowsRecordSources.query. \
        filter(WorkflowsRecordSources.record_id == head_uuid). \
        filter(WorkflowsRecordSources.source != 'arxiv'). \
        one_or_none()

    if publisher_root:
        return 'publisher'

    arxiv_root = get_root(source='arxiv', uuid=head_uuid)
    if arxiv_root:
        return 'arxiv'

    return None
