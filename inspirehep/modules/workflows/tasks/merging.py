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

from flask import current_app

from inspire_json_merger.api import merge
from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.models import WorkflowsRecordSources
from inspirehep.modules.workflows.utils import (
    get_resolve_merge_conflicts_callback_url,
    with_debug_logging
)


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
    roots_sources = set(
        r.source for r in
        WorkflowsRecordSources.query.filter_by(record_id=head_uuid).all()
    )

    if not roots_sources:
        return None

    return 'arxiv' if 'arxiv' in roots_sources else 'publisher'


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
        For the time being the ``root`` will be ignored, and we'll rely only
        on the ``head``, hence it is a rootless implementation. Also when
        the feature flag ``FEATURE_FLAG_ENABLE_MERGER`` is ``False`` it
        will skip the merge.

    """
    if not current_app.config.get('FEATURE_FLAG_ENABLE_MERGER'):
        return None

    matched_control_number = obj.extra_data['matches']['approved']

    head_uuid = PersistentIdentifier.get(
        'lit', matched_control_number).object_uuid

    obj.extra_data['head_uuid'] = str(head_uuid)

    head = InspireRecord.get_record(head_uuid)
    root = {}
    update = obj.data

    merged, conflicts = merge(
        head=head.dumps(),
        root=root,
        update=update
    )

    obj.data = merged

    if conflicts:
        obj.extra_data['conflicts'] = conflicts
        obj.extra_data['callback_url'] = \
            get_resolve_merge_conflicts_callback_url()
    obj.save()
