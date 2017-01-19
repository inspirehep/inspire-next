# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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

"""Model for WorkflowsAudit."""

from __future__ import absolute_import, division, print_function

import requests
import json

from flask import current_app

from .models import WorkflowsAudit


def json_api_request(url, data, headers=None):
    """Make JSON API request and return JSON response."""
    final_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if headers:
        final_headers.update(headers)
    current_app.logger.debug("POST {0} with \n{1}".format(
        url, json.dumps(data, indent=4)
    ))
    try:
        response = requests.post(
            url=url,
            headers=final_headers,
            data=json.dumps(data),
            timeout=30
        )
    except requests.exceptions.RequestException as err:
        current_app.logger.exception(err)
        raise
    if response.status_code == 200:
        return response.json()


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
