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

from copy import deepcopy
from flask import current_app

from inspire_json_merger.api import merge
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import (
    get_resolve_merge_conflicts_callback_url,
    read_wf_record_source,
    with_debug_logging
)

from inspirehep.utils.record import get_source


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

    head_uuid = PersistentIdentifier.get(
        'lit', matched_control_number).object_uuid

    obj.extra_data['head_uuid'] = str(head_uuid)

    head = InspireRecord.get_record(head_uuid)
    update = obj.data
    update_source = get_source(update).lower()
    head_root = read_wf_record_source(record_uuid=head.id, source=update_source)
    head_root = head_root.json if head_root else {}

    obj.extra_data['merger_head_revision'] = head.revision_id
    obj.extra_data['merger_original_root'] = deepcopy(head_root)

    merged, conflicts = merge(
        head=head.dumps(),
        root=head_root,
        update=update,
    )

    obj.data = merged

    if conflicts:
        obj.extra_data['conflicts'] = conflicts
        obj.extra_data['callback_url'] = \
            get_resolve_merge_conflicts_callback_url()
    obj.save()
