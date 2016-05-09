# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Model for WorkflowsAudit."""

from __future__ import absolute_import, print_function

import os

from flask import current_app

from .models import WorkflowsAudit


def get_storage_path(suffix=""):
    """Return workflow storage path."""
    storage_path = os.path.join(
        current_app.config.get(
            'WORKFLOWS_STORAGEDIR',
            current_app.config.get('CFG_TMPSHAREDDIR')
        ),
        suffix
    )
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path


def log_workflows_action(action, prediction_results,
                         object_id, user_id,
                         source, user_action=""):
    """Log the action taken by user compared to a prediction."""
    if prediction_results:
        score = prediction_results.get("max_score")  # returns 0.222113
        decision = prediction_results.get("decision")  # returns "Rejected"

        # Map actions to align with the prediction format
        action_map = {
            'accept': 'Non-CORE',
            'accept_core': 'CORE',
            'reject': 'Rejected'
        }

        logging_info = {
            'object_id': object_id,
            'user_id': user_id,
            'score': score,
            'user_action': action_map.get(user_action, ""),
            'decision': decision,
            'source': source,
            'action': action
        }
        audit = WorkflowsAudit(**logging_info)
        audit.save()
