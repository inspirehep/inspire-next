# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014. 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Signal receivers for workflows."""

from invenio_workflows.signals import (
    workflow_halted
)


def continue_workflow(sender, **kwargs):
    """Continue a workflow object if halted at a specific task."""
    if hasattr(sender, "last_task"):
        task = sender.last_task
        if task == 'halt_to_render':
            sender.continue_workflow(delayed=True)


def precache_holdingpen_row(sender, **kwargs):
    """Precache a Holding Pen row."""
    from invenio_workflows.utils import get_formatted_holdingpen_object
    # Call it to cache it
    get_formatted_holdingpen_object(sender)


workflow_halted.connect(precache_holdingpen_row)
workflow_halted.connect(continue_workflow)
