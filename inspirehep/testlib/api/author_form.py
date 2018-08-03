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

"""Literature suggestion form testlib."""

from __future__ import absolute_import, division, print_function


class AuthorFormInputData(object):
    def __init__(
        self,
        given_names,
        research_field,
        status='active',
        family_name=None,
        display_name=None
    ):
        self.given_names = given_names
        self.family_name = family_name
        self.display_name = display_name
        self.status = status
        self.research_field = research_field

    def request_data(self):
        formdata = {
            'given_names': self.given_names,
            'family_name': self.family_name,
            'display_name': self.display_name,
            'status': self.status,
            'research_field': self.research_field,
        }

        return formdata


class AuthorFormApiClient(object):
    SUBMIT_AUTHOR_FORM_URL = '/authors/new/submit'

    def __init__(self, client):
        self._client = client

    def submit(self, form_input_data):
        response = self._client.post(
            self.SUBMIT_AUTHOR_FORM_URL,
            data=form_input_data.request_data()
        )
        response.raise_for_status()
        return response
