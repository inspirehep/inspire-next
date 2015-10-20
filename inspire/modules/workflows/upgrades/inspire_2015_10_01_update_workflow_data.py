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

    def rename_object_action(obj):
        if obj.get_action() == "arxiv_approval":
            obj.set_action("hep_approval", obj.get_action_message())

    def reset_workflow_object_states(obj):
        """Fix workflow positions and states.

        Old states from Prod/QA:
        {(), (0,), (5, 3, 14), (5, 3, 14, 0), (5, 3, 15), (5, 3, 15, 1)}

        {(),
         (0,),
         (5,),
         (5, 3, 1),
         (5, 3, 10),
         (5, 3, 11),
         (5, 3, 12),
         (5, 3, 14),
         (5, 3, 14, 0),
         (6, 3, 4)}

        OLD -> NEW
        5, 3, 14 -> 0 end
        5, 3, 10 -> 14, 0 halted
        """
        pos = obj.get_current_task()
        if obj.version == ObjectVersion.COMPLETED:
            obj.save(task_counter=[len(workflows.get(obj.workflow.name).workflow) - 1])
            return
        elif obj.version == ObjectVersion.RUNNING:
            # Running? Nah that cannot be.
            obj.version = ObjectVersion.ERROR
        try:
            obj.get_current_task_info()
        except IndexError:
            # The current task counter is Invalid
            obj.version = ObjectVersion.ERROR

        if obj.workflow.name == "process_record_arxiv":
            if tuple(pos) in [
                    (5,), (5, 3, 14), (5, 3, 14, 0), (5, 3, 15), (5, 3, 15, 1)]:
                pos = [len(workflows.get(obj.workflow.name).workflow) - 1]  # finished
            elif tuple(pos) in [(5, 3, 10), (5, 3, 11), (5, 3, 12)]:
                pos = [14, 0]  # halted
            elif len(pos) > 1 and pos[0] == 6:
                # We need to update pos from 6 to start of pre_processing part
                pos = [7]
            else:
                pos = [0]  # Nothing here, we go to start
            obj.save(task_counter=pos)

    # Special submission handling
    for deposit in BibWorkflowObject.query.filter(
            BibWorkflowObject.module_name == "webdeposit"):
        reset_workflow_object_states(deposit)
        d = Deposition(deposit)
        sip = d.get_latest_sip()
        if sip:
            sip.metadata = bibfield.do(sip.metadata)
            sip.package = legacy_export_as_marc(hep2marc.do(sip.metadata))
            d.update()
        deposit.save()

    # Special workflow handling
    workflows_to_fix = ["process_record_arxiv"]
    workflow_objects = []
    for workflow_name in workflows_to_fix:
        workflow_objects += BibWorkflowObject.query.join(
            BibWorkflowObject.workflow).filter(Workflow.name == workflow_name).all()

    for obj in workflow_objects:
        metadata = obj.get_data()
        reset_workflow_object_states(obj)
        rename_object_action(obj)
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
