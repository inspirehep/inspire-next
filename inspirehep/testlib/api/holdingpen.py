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

import subprocess

from inspirehep.testlib.api.base_resource import BaseResource


class HoldingpenResource(BaseResource):
    """Inspire holdingpen entry to represent a workflow"""

    def __init__(self, workflow_id, approved, is_update, core, status, title, doi=None, arxiv_eprint=None, control_number=None):
        self.approved = approved
        self.is_update = is_update
        self.core = core
        self.status = status
        self.workflow_id = workflow_id
        self.control_number = control_number
        self.title = title
        self.arxiv_eprint = arxiv_eprint
        self.doi = doi

    @classmethod
    def from_json(cls, json, workflow_id=None):
        """
        Args:
            json(dict): dictionary of a single entry as returned by the api.
        """
        if workflow_id is None:
            workflow_id = json['id']

        extra_data = json.get('_extra_data', {})

        hp_enty = cls(
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
        hp_enty._raw_json = json
        return hp_enty


class HoldingpenApiClient(object):
    """Client for the Inspire Holdingpen"""
    HOLDINGPEN_API_URL = '/api/holdingpen/'

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
