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

import os

import pkg_resources
import requests
import requests_mock

from inspirehep.modules.workflows.utils import download_file_to_workflow

from mocks import MockFiles, MockObj


def test_download_file_to_workflow_retries_on_protocol_error():
    with requests_mock.Mocker() as requests_mocker:
        filename = pkg_resources.resource_filename(
            __name__, os.path.join('fixtures', '1605.03844.pdf'))

        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844', [
                {'exc': requests.packages.urllib3.exceptions.ProtocolError},
                {'body': filename, 'status_code': 200},
            ])

        data = {}
        extra_data = {}
        files = MockFiles({})

        obj = MockObj(data, extra_data, files=files)

        expected = {'key': '1605.03844.pdf'}
        result = download_file_to_workflow(
            obj, '1605.03844.pdf', 'http://export.arxiv.org/pdf/1605.03844')

        assert expected == result
