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


class LiteratureFormInputData(object):
    def __init__(self, title, language='en', type_of_doc='article'):
        self.type_of_doc = type_of_doc
        self.title = title
        self.language = language
        self.authors = []

    def add_author(self, name, affiliation=None):
        self.authors.append({
            'name': name,
            'affiliation': affiliation,
        })

    def _authors_request_data(self):
        formdata = {
            'authors-__last_index__': len(self.authors) - 1,
        }

        for idx, author in enumerate(self.authors):
            formdata['authors-{}-name'.format(idx)] = author['name']
            formdata['authors-{}-affiliation'.format(idx)] = author['affiliation']

        return formdata

    def request_data(self):
        formdata = {
            'type_of_doc': self.type_of_doc,
            'language': self.language,
            'title': self.title,
        }

        formdata.update(self._authors_request_data())

        return formdata


class LiteratureFormApiClient(object):
    SUBMIT_LITERATURE_FORM_URL = '/literature/new/submit'

    def __init__(self, client):
        self._client = client

    def submit(self, form_input_data):
        response = self._client.post(
            self.SUBMIT_LITERATURE_FORM_URL,
            data=form_input_data.request_data()
        )
        response.raise_for_status()
        return response
