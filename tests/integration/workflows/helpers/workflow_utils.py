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

from __future__ import absolute_import, division, print_function

import time

from datetime import datetime, timedelta
import uuid
from copy import deepcopy

from invenio_db import db
from invenio_workflows import workflow_object_class, Workflow


def build_workflow(workflow_data, data_type='hep', extra_data=None, status=None, **kwargs):
    extra_data = extra_data or {}
    if 'source_data' not in extra_data:
        extra_data['source_data'] = {
            'data': deepcopy(workflow_data),
            'extra_data': deepcopy(extra_data),
        }
    wf = Workflow(name='article', extra_data=extra_data, uuid=uuid.uuid4())
    wf.save()
    workflow_object = workflow_object_class.create(
        data=workflow_data,
        data_type=data_type,
        extra_data=extra_data,
        **kwargs
    )
    if status:
        workflow_object.status = status
    workflow_object.save(id_workflow=wf.uuid)

    return workflow_object


def check_wf_state(workflow_id, desired_status, max_time=800):
    """Waits for the workflow to go to desired status
    Args:
        workflow: workflow to check
        desired_state: desired state
        max_time: maximum time to wait in seconds, otherwise raise exception
    Returns: None
    """
    start = datetime.now()
    end = start + timedelta(seconds=max_time)
    while True:
        db.session.close()
        if workflow_object_class.get(workflow_id).status == desired_status:
            return
        if datetime.now() > end:
            raise AssertionError(
                "Status for workflow: %s didn't changed to %s for %s seconds" % (
                    workflow_id, desired_status, max_time
                )
            )
        time.sleep(5)
