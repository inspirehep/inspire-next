# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Utils for data migration from INSPIRE legacy instance."""

from __future__ import absolute_import, print_function


def rename_object_action(obj):
    if obj.get_action() == "arxiv_approval":
        obj.set_action("hep_approval", obj.get_action_message())


def reset_workflow_object_states(obj):
    """Fix workflow positions and states.

    Old states from Prod/QA:
    {(),
     (0,),
     (3, 0),
     (5, 3, 11, 0),
     (5, 3, 14),
     (5, 3, 14, 0),
     (5, 3, 15),
     (5, 3, 15, 1)}

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
    from invenio_workflows.models import ObjectVersion
    from invenio_workflows.registry import workflows

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
        elif tuple(pos) in [(5, 3, 10), (5, 3, 11, 0), (5, 3, 12)]:
            pos = [14, 0]  # halted
        elif tuple(pos) == (3, 0):
            pos = [4, 0]  # deleted
        elif len(pos) > 1 and pos[0] == 6:
            # We need to update pos from 6 to start of pre_processing part
            pos = [7]
        else:
            pos = [0]  # Nothing here, we go to start
        return pos
