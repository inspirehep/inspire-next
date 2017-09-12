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

from inspirehep.modules.workflows.models import WorkflowsRecordSources


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
