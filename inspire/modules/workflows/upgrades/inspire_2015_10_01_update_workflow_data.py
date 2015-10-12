# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Migrate bibfield data model to new doJSON data model in workflows."""

from __future__ import absolute_import, print_function, unicode_literals

import six


depends_on = []


def info():
    """Info about this upgrade."""
    return __doc__


def do_upgrade():
    """Implement your upgrades here."""
    from invenio_workflows.models import (
        BibWorkflowObject,
        Workflow,
        ObjectVersion
    )
    from invenio_workflows.registry import workflows
    from invenio_deposit.models import Deposition

    from inspire.dojson.utils import legacy_export_as_marc
    from inspire.dojson.hep import hep2marc
    from inspire.modules.workflows.dojson import bibfield
    from inspire.modules.workflows.models import Payload

    def reset_workflow_object_states(obj):
        if obj.version == 1:
            obj.save(task_counter=[len(workflows.get(obj.workflow.name).workflow) - 1])
        elif obj.version == 3:
            # Running? Nah that cannot be.
            obj.save(version=ObjectVersion.ERROR)
        try:
            obj.get_current_task_info()
        except IndexError:
            # The current task counter is Invalid
            obj.save(version=ObjectVersion.ERROR)

        if obj.workflow.name == "process_record_arxiv":
            pos = obj.get_current_task()
            if tuple(pos) == (5, 3, 14):
                pos = [6, 3, 14, 0]
            elif len(pos) > 1 and pos[0] == 5:
                # We need to update pos from 5 to 6
                pos = [6] + list(pos)[1:]
            obj.save(task_counter=pos)

    # Special submission handling
    for deposit in BibWorkflowObject.query.filter(
            BibWorkflowObject.module_name == "webdeposit"):
        d = Deposition(deposit)
        sip = d.get_latest_sip()
        if sip:
            sip.metadata = bibfield.do(sip.metadata)
            sip.package = legacy_export_as_marc(hep2marc.do(sip.metadata))
            d.save()
        reset_workflow_object_states(deposit)

    # Special workflow handling
    workflows_to_fix = ["process_record_arxiv"]
    workflow_objects = []
    for workflow_name in workflows_to_fix:
        workflow_objects += BibWorkflowObject.query.join(
            BibWorkflowObject.workflow).filter(Workflow.name == workflow_name).all()

    for obj in workflow_objects:
        metadata = obj.get_data()
        reset_workflow_object_states(obj)
        if isinstance(metadata, six.string_types):
            # Ignore records that have string as data
            continue
        if 'drafts' in metadata:
            # New data model detected
            continue
        if hasattr(metadata, 'dumps'):
            metadata = metadata.dumps(clean=True)
        obj.data = bibfield.do(metadata)
        payload = Payload.create(
            type=obj.workflow.name,
            workflow_object=obj
        )
        payload.save()


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    from invenio_workflows.models import BibWorkflowObject
    return BibWorkflowObject.query.count()


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    pass


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    pass
