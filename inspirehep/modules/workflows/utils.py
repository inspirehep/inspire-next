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

from __future__ import absolute_import, division, print_function

import json
import logging
import traceback
from functools import wraps

import requests
from flask import current_app

from .models import WorkflowsAudit


LOGGER = logging.getLogger(__name__)


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


def with_debug_logging(func):
    """Generate a debug log with info on what's going to
    run.

    It tries it's best to use the logging facilities of the object passed or
    the application context before falling back to the python logging facility.

    """
    @wraps(func)
    def _decorator(*args, **kwargs):
        def _get_obj(args, kwargs):
            if args:
                obj = args[0]
            else:
                obj = kwargs.get('obj', kwargs.get('record'))
            return obj

        def _get_logfn(args, kwargs):
            obj = _get_obj(args, kwargs)
            if hasattr(obj, 'log') and hasattr(obj.log, 'debug'):
                logfn = obj.log.debug
            elif hasattr(current_app, 'log'):
                logfn = current_app.log.debug
            else:
                logfn = LOGGER.debug

            return logfn

        def _proof_run(func, *args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                LOGGER.debug(
                    "Error while trying to log with %s:\n%s",
                    logfn,
                    traceback.format_exc()
                )

        logfn = _get_logfn(args, kwargs)

        _proof_run(logfn, "Starting %s", func)
        res = func(*args, **kwargs)
        _proof_run(
            logfn,
            "Finished %s with (single quoted) result '%s'",
            func,
            res,
        )

        return res

    return _decorator
