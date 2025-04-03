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
from datetime import datetime

from copy import deepcopy
from flask import current_app
from idutils import is_arxiv_post_2007
from json_merger.errors import MaxThresholdExceededError

from inspire_json_merger.api import merge
from inspire_schemas.readers import LiteratureReader
from inspire_utils.record import get_value
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import (
    get_resolve_merge_conflicts_callback_url,
    read_wf_record_source,
    with_debug_logging, get_record_from_hep
)
from inspirehep.modules.workflows.tasks.actions import error_workflow


@with_debug_logging
def has_conflicts(obj, eng):
    """Return if the workflow has any confilicts."""
    return obj.extra_data.get('conflicts')


@with_debug_logging
def merge_articles(obj, eng):
    """Merge two articles.

    The workflow payload is overwritten by the merged record, the conflicts are
    stored in ``extra_data.conflicts``. Also, it adds a ``callback_url`` which
    contains the endpoint which resolves the merge conflicts.

    Note:
        When the feature flag ``FEATURE_FLAG_ENABLE_MERGER`` is ``False`` it
        will skip the merge.

    """
    if not current_app.config.get('FEATURE_FLAG_ENABLE_MERGER'):
        return None

    matched_control_number = obj.extra_data['matches']['approved']

    update = obj.data
    update_source = LiteratureReader(obj.data).source
    if current_app.config.get('FEATURE_FLAG_ENABLE_HEP_REST_RECORD_PULL'):
        record_data = get_record_from_hep("lit", matched_control_number)
        head_uuid = record_data['uuid']
        head_record = record_data['metadata']
        head_revision_id = record_data['revision_id']
        head_version_id = head_revision_id + 1
    else:
        head_uuid = PersistentIdentifier.get(
            'lit', matched_control_number).object_uuid
        head_record = InspireRecord.get_record(head_uuid)
        head_version_id = head_record.model.version_id
        head_revision_id = head_record.revision_id
        head_record = head_record.to_dict()

    head_root = read_wf_record_source(record_uuid=head_uuid, source=update_source.lower())

    # TODO: remove check when we'll use hep on prod
    if current_app.config.get('FEATURE_FLAG_USE_ROOT_TABLE_ON_HEP'):
        head_root = deepcopy(head_root['json'] if head_root else {})
    else:
        head_root = deepcopy(head_root.json if head_root else {})

    obj.extra_data['head_uuid'] = str(head_uuid)
    obj.extra_data['head_version_id'] = head_version_id
    obj.extra_data['merger_head_revision'] = head_revision_id
    obj.extra_data['merger_original_root'] = head_root

    try:
        merged, conflicts = merge(
            head=head_record,
            root=head_root,
            update=update,
        )
    except MaxThresholdExceededError:
        error_workflow('Conflict resolution failed. Max threshold exceeded.')

    obj.data = merged

    if conflicts:
        obj.extra_data['conflicts'] = conflicts
        obj.extra_data['conflicts_metadata'] = {
            'datetime': datetime.now().strftime("%b %d, %Y, %H:%M:%S %p"),
            'update_source': update_source,
        }
        obj.extra_data['callback_url'] = \
            get_resolve_merge_conflicts_callback_url()
    obj.save()


def conflicts_ticket_context(user, obj):
    server_name = current_app.config['SERVER_NAME']
    workflow_id = obj.id
    arxiv_ids = get_value(obj.data, 'arxiv_eprints.value') or []
    for index, arxiv_id in enumerate(arxiv_ids):
        if arxiv_id and is_arxiv_post_2007(arxiv_id):
            arxiv_ids[index] = 'arXiv:{0}'.format(arxiv_id)
    report_numbers = get_value(obj.data, 'report_numbers.value') or []
    dois = [
        "doi:{0}".format(doi)
        for doi in get_value(obj.data, 'dois.value') or []
    ]
    recid = obj.extra_data.get('recid')
    subject = ' '.join(filter(
        lambda x: x is not None,
        arxiv_ids + dois + report_numbers + ['(#{0})'.format(recid)]
    ))

    return dict(
        server_name=server_name,
        workflow_id=workflow_id,
        arxiv_ids=arxiv_ids,
        dois=dois,
        recid=recid,
        report_numbers=report_numbers,
        subject=subject
    )
