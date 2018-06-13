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

from invenio_workflows.errors import WorkflowsError


class DownloadError(WorkflowsError):

    """Error representing a failed download in a workflow."""


class MergeError(WorkflowsError):

    """Error representing a failed merge in a workflow."""


class CallbackError(WorkflowsError):
    """Callback exception."""

    code = 400
    error_code = 'CALLBACK_ERROR'
    errors = None
    message = 'Workflow callback error.'
    workflow = None

    def to_dict(self):
        """Execption to dictionary."""
        response = {}
        response['error_code'] = self.error_code
        if self.errors is not None:
            response['errors'] = self.errors
        response['message'] = self.message
        if self.workflow is not None:
            response['workflow'] = self.workflow
        return response


class CallbackMalformedError(CallbackError):
    """Malformed request exception."""

    error_code = 'MALFORMED'
    message = 'The workflow request is malformed.'

    def __init__(self, errors=None, **kwargs):
        """Initialize exception."""
        super(CallbackMalformedError, self).__init__(**kwargs)
        self.errors = errors


class CallbackWorkflowNotFoundError(CallbackError):
    """Workflow not found exception."""

    code = 404
    error_code = 'WORKFLOW_NOT_FOUND'

    def __init__(self, workflow_id, **kwargs):
        """Initialize exception."""
        super(CallbackWorkflowNotFoundError, self).__init__(**kwargs)
        self.message = 'The workflow with id "{}" was not found.'.format(
            workflow_id)


class CallbackValidationError(CallbackError):
    """Validation error exception."""

    error_code = 'VALIDATION_ERROR'
    message = 'Validation error.'

    def __init__(self, workflow_data, **kwargs):
        """Initialize exception."""
        super(CallbackValidationError, self).__init__(**kwargs)
        self.workflow = workflow_data


class CallbackWorkflowNotInValidationError(CallbackError):
    """Validation workflow not in validation error exception."""

    error_code = 'WORKFLOW_NOT_IN_ERROR_STATE'

    def __init__(self, workflow_id, **kwargs):
        """Initialize exception."""
        super(CallbackWorkflowNotInValidationError, self).__init__(**kwargs)
        self.message = 'Workflow {} is not in validation error state.'.format(
            workflow_id)


class CallbackWorkflowNotInMergeState(CallbackError):
    """Workflow not in validation error exception."""

    error_code = 'WORKFLOW_NOT_IN_MERGE_STATE'

    def __init__(self, workflow_id, **kwargs):
        """Initialize exception."""
        super(CallbackWorkflowNotInMergeState, self).__init__(**kwargs)
        self.message = 'Workflow {} is not in merge state.'.format(
            workflow_id)


class CallbackWorkflowNotInWaitingEditState(CallbackError):
    """Workflow not in validation error exception."""

    error_code = 'WORKFLOW_NOT_IN_WAITING_FOR_CURATION_STATE'

    def __init__(self, workflow_id, **kwargs):
        """Initialize exception."""
        super(CallbackWorkflowNotInWaitingEditState, self).__init__(**kwargs)
        self.message = 'Workflow {} is not in waiting for curation state.'.\
            format(workflow_id)


class CallbackRecordNotFoundError(CallbackError):
    """Record not found exception."""

    code = 404
    error_code = 'RECORD_NOT_FOUND'

    def __init__(self, recid, **kwargs):
        """Initialize exception."""
        super(CallbackRecordNotFoundError, self).__init__(**kwargs)
        self.message = 'The record with id "{}" was not found.'.format(recid)
