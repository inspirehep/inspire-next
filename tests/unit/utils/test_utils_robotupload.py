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

import pytest
import requests_mock
from flask import current_app
from mock import patch

from inspirehep.utils.robotupload import make_robotupload_marcxml


def test_make_robotupload_marcxml():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://localhost:5000/batchuploader/robotupload/insert'
        )

        make_robotupload_marcxml(
            'http://localhost:5000', '<record></record>', 'insert')


def test_make_robotupload_marcxml_falls_back_to_config_when_url_is_none():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://inspirehep.net/batchuploader/robotupload/insert'
        )

        config = {'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net'}

        with patch.dict(current_app.config, config):
            make_robotupload_marcxml(None, '<record></record>', 'insert')


def test_make_robotupload_marcxml_raises_when_url_is_none_and_config_is_empty():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://localhost:5000/batchuploader/robotupload/insert'
        )

        with pytest.raises(ValueError) as excinfo:
            make_robotupload_marcxml(None, '<record></record>', 'insert')
        assert 'LEGACY_ROBOTUPLOAD_URL' in str(excinfo.value)


def test_make_robotupload_marcxml_handles_unicode():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://localhost:5000/batchuploader/robotupload/insert'
        )

        snippet = (
            u'<record>'
            u'  <datafield tag="700" ind1=" " ind2=" ">'
            u'    <subfield code="a">André, M.</subfield>'
            u'  </datafield>'
            u'</record>'
        )  # record/1503367

        make_robotupload_marcxml('http://localhost:5000', snippet, 'insert')


def test_make_robotupload_marcxml_handles_non_unicode():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'POST', 'http://localhost:5000/batchuploader/robotupload/insert'
        )

        snippet = (
            u'<record>'
            u'  <datafield tag="700" ind1=" " ind2=" ">'
            u'    <subfield code="a">André, M.</subfield>'
            u'  </datafield>'
            u'</record>'
        ).encode('utf-8')  # record/1503367

        make_robotupload_marcxml('http://localhost:5000', snippet, 'insert')
