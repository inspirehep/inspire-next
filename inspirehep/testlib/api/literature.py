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

"""/literature endpoint api client and resources."""

from __future__ import absolute_import, division, print_function


from inspirehep.testlib.api.base_resource import BaseResource


class LiteratureResource(BaseResource):
    """Inspire base entry to represent a literature record"""
    def __init__(self, control_number, doi, arxiv_eprint, title):
        self.control_number = control_number
        self.doi = doi
        self.arxiv_eprint = arxiv_eprint
        self.title = title

    @classmethod
    def from_json(cls, json):
        """
        Args:
            json(dict): dictionary of a single entry as returned by the api.
        """
        lit = cls(
            control_number=json['metadata'].get('control_number'),
            doi=json['metadata'].get('dois', [{}])[0].get('value'),
            arxiv_eprint=json['metadata'].get('arxiv_eprints', [{}])[0].get('value'),
            title=json['metadata']['titles'][0]['title'],
        )
        lit._raw_json = json
        return lit


class LiteratureApiClient(object):
    """Client for the Inspire Literature section"""
    LITERATURE_API_URL = '/api/literature/'

    def __init__(self, client):
        self._client = client

    def get_record(self, rec_id):
        resp = self._client.get(self.LITERATURE_API_URL, str(rec_id))
        resp.raise_for_status()
        return LiteratureResource.from_json(resp.json())
