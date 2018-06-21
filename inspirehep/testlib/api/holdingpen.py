# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""/holdingpen endopint api client and resources."""

from __future__ import absolute_import, division, print_function

import copy
import subprocess
from urlparse import urlparse

from inspirehep.testlib.api.base_resource import BaseResource


class HoldingpenResource(BaseResource):
    """Inspire holdingpen entry to represent a workflow"""

    def __init__(self, workflow_id, approved, is_update, core, status, title, doi=None, arxiv_eprint=None, control_number=None):
        """
        Don't use this constructor yet unless you know what you are doing, use
        `from_json` instead as this one does not create a full holdingpen entry.

        """
        self.approved = approved
        self.is_update = is_update
        self.core = core
        self.status = status
        self.workflow_id = workflow_id
        self.control_number = control_number
        self.title = title
        self.arxiv_eprint = arxiv_eprint
        self.doi = doi
        self._raw_json = None

    @classmethod
    def from_json(cls, json, workflow_id=None):
        """
        Construcor for a holdingpen entry, it will be able to be mapped to and
        from json, and used to fully edit entries. Usually you pass to it the
        full raw json from the details of a holdingpen entry.

        Args:
            json(dict): dictionary of a single entry as returned by the api.
        """
        if workflow_id is None:
            workflow_id = json['id']

        extra_data = json.get('_extra_data', {})

        hp_entry = cls(
            workflow_id=workflow_id,
            approved=extra_data.get('approved'),
            is_update=extra_data.get('is-update'),
            core=extra_data.get('core'),
            status=json['_workflow']['status'],
            title=json['metadata']['titles'][0]['title'],
            control_number=json['metadata'].get('control_number'),
            arxiv_eprint=json['metadata'].get('arxiv_eprints', [{}])[0].get('value'),
            doi=json['metadata'].get('dois', [{}])[0].get('value'),
        )
        hp_entry._raw_json = json
        return hp_entry

    def to_json(self):
        """
        Translates the current entry to a json applying any changes to the
        original json passed, or just with the info added to the entry since
        it's instantiation.

        Returns:
            json: Json view of the current status of the entry.
        """
        new_json = copy.deepcopy(self._raw_json or {})

        new_extra_data = {
            'approved': self.approved,
            'is_update': self.is_update,
            'core': self.core,
        }
        new_json['_extra_data'].update(new_extra_data)
        new_json['workflow_id'] = self.workflow_id,
        new_json['metadata']['titles'][0]['title'] = self.title
        new_json['_workflow']['status'] = self.status

        if self.control_number is not None:
            new_json['metadata']['control_number'] = self.control_number

        if self.arxiv_eprint is not None:
            new_json['metadata']['arxiv_eprints'][0]['value'] = self.arxiv_eprint

        if self.doi is not None:
            new_json['metadata']['dois'][0]['value'] = self.doi

        return new_json


class HoldingpenApiClient(object):
    """Client for the Inspire Holdingpen"""
    HOLDINGPEN_API_URL = '/api/holdingpen/'
    HOLDINGPEN_EDIT_URL = '/api/holdingpen/{workflow_id}/action/edit'
    HOLDINGPEN_RESOLVE_URL = '/api/holdingpen/{workflow_id}/action/resolve'

    def __init__(self, client):
        self._client = client

    def get_list_entries(self):
        resp = self._client.get(self.HOLDINGPEN_API_URL)
        resp.raise_for_status()
        return [
            HoldingpenResource.from_json(json=hit['_source'], workflow_id=hit['_id'])
            for hit in resp.json()['hits']['hits']
        ]

    def get_detail_entry(self, holdingpen_id):
        resp = self._client.get(self.HOLDINGPEN_API_URL, str(holdingpen_id))
        resp.raise_for_status()
        return HoldingpenResource.from_json(resp.json())

    def _edit_workflow(self, holdingpen_entry):
        """
        Helper method to edit a holidngpen entry.

        Args:
            holdingpen_entry(HoldingpenResource): entry updated with the
                already changed data.

        Returns:
            requests.Response: The actual http response to the last call (the
                actual /resolve endpoint).

        Raises:
            requests.exceptions.BaseHttpError: any error related to the http
                calls made.

        Example:
            >>> my_entry = holdingpen_client.get_detail_entry(holdingpen_id=1234)
            >>> my_entry.core = False   # do some changes
            >>> holdingpen_client._edit_workflow(holdingpen_entry=my_entry)
            <Response [200]>

        """

        edit_response = self._client.post(
            self.HOLDINGPEN_EDIT_URL.format(workflow_id=holdingpen_entry.workflow_id),
            json=holdingpen_entry.to_json(),
        )
        edit_response.raise_for_status()
        return edit_response

    def _resolve_workflow(self, holdingpen_entry, resolution_data):
        """
        Helper method to resolve a workflow action, for more details see:
            https://github.com/inveniosoftware-contrib/invenio-workflows-ui/blob/master/invenio_workflows_ui/api.py#L272

        Args:
            holdingpen_id(int): id of the holdingpen entry to accept.
            resolution_data(dict): Data to pass to the resolve endpoint.

        Returns:
            requests.Response: The actual http response to the last call (the
                actual /resolve endpoint).
        Raises:
            requests.exceptions.BaseHttpError: any error related to the http
                calls made.

        Example:
            >>> holdingpen_client._resolve_workflow(
                holdingpen_id=12345,
                resolution_data={
                    'pdf_upload': false,
                    'reason': '',
                    'value': 'accept_core',
                }
            )
            <Response [200]>
        """
        resolve_response = self._client.post(
            self.HOLDINGPEN_RESOLVE_URL.format(workflow_id=holdingpen_entry.workflow_id),
            json=resolution_data,
        )
        resolve_response.raise_for_status()
        return resolve_response

    def _resolve_hep_approval(self, holdingpen_id, approval_type, reason=''):
        """
        Args:
            holdingpen_id(int): id of the holdingpen entry to accept.
            approval_type(str): Approval resolution, currently one of
                'accept_core', 'accept_non_core' or 'reject'
            reason(str): If it was rejected, the reason explaining why.
            pdf_upload(bool): If a new pdf was uploadad

        Returns:
            requests.Response: the response to the last 'resolve' api call.
        """
        resolution_data = {
            'pdf_upload': False,
            'reason': reason,
            'value': approval_type,
        }

        entry_to_accept = self.get_detail_entry(holdingpen_id=holdingpen_id)
        # This call is not really changing anyting, but the ui does it always
        # just in case there are modifications through the ui (not the editor)
        # made to the workflow, so we do the same in the tests.
        self._edit_workflow(holdingpen_entry=entry_to_accept)

        resolve_response = self._resolve_workflow(
            holdingpen_entry=entry_to_accept,
            resolution_data=resolution_data,
        )
        return resolve_response

    def resume_wf(self, hp_entry):
        full_callback_url = hp_entry._raw_json['_extra_data']['callback_url']
        callback_url = urlparse(full_callback_url).path

        payload = {
            'id': hp_entry.workflow_id,
            'metadata': hp_entry._raw_json['metadata'],
            '_extra_data': hp_entry._raw_json['_extra_data']
        }
        res = self._client.put(callback_url, json=payload)
        res.raise_for_status()
        return res

    def accept_core(self, holdingpen_id):
        res = self._resolve_hep_approval(
            holdingpen_id=holdingpen_id,
            approval_type='accept_core'
        )
        return res

    def accept_non_core(self, holdingpen_id):
        res = self._resolve_hep_approval(
            holdingpen_id=holdingpen_id,
            approval_type='accept_non_core'
        )
        return res

    def reject(self, holdingpen_id):
        res = self._resolve_hep_approval(
            holdingpen_id=holdingpen_id,
            approval_type='reject'
        )
        return res

    def run_harvest(self, spider, workflow='article', **kwargs):
        """Run a harvest scheduling a job in celery"""
        run_harvest = 'inspirehep crawler schedule %s %s %s' % (
            spider,
            workflow,
            ' '.join('--kwarg %s=%s' % (k, v) for k, v in kwargs.items()),
        )

        assert subprocess.check_output(
            run_harvest.split(),
            stderr=subprocess.STDOUT
        )
