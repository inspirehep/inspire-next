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

"""API entries for Inspire API clients"""

from __future__ import absolute_import, division, print_function


class LiteratureEntry(object):
    """Inspire base entry for representing a literature record"""
    def __init__(self, json):
        self.control_number = json['metadata'].get('control_number')
        self.doi = json['metadata'].get('dois', [{}])[0].get('value')
        self.arxiv_eprint = json['metadata'].get('arxiv_eprints', [{}])[0]['value']
        self.title = json['metadata']['titles'][0]['title']

    def __repr__(self):
        return str(self.__dict__)


class HoldingpenEntry(LiteratureEntry):
    """Inspire holdingpen entry for representing a workflow"""

    def __init__(self, json, id=None):
        super(self.__class__, self).__init__(json)

        if not json.get('_extra_data'):
            json['_extra_data'] = {}

        self.raw_content = json

        self.approved = json['_extra_data'].get('approved')
        self.is_update = json['_extra_data'].get('is-update', False)
        self.core = json['_extra_data'].get('core', False)

        self.status = json['_workflow']['status']
        self.workflow_id = id
