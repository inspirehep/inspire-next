# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import httpretty
import pytest
from mock import patch

from inspirehep.utils.robotupload import make_robotupload_marcxml


@pytest.mark.httpretty
def test_make_robotupload_marcxml():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://localhost:5000/batchuploader/robotupload/insert')

    make_robotupload_marcxml(
        'http://localhost:5000', '<record></record>', 'insert')

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_make_robotupload_marcxml_falls_back_to_config_when_url_is_none(app):
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://inspirehep.net/batchuploader/robotupload/insert')

    config = {'LEGACY_ROBOTUPLOAD_URL': 'http://inspirehep.net'}

    with app.app_context():
        with patch.dict(app.config, config):
            make_robotupload_marcxml(None, '<record></record>', 'insert')

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_make_robotupload_marcxml_raises_when_url_is_none_and_config_is_empty():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://localhost:5000/batchuploader/robotupload/insert')

    with pytest.raises(ValueError) as excinfo:
        make_robotupload_marcxml(None, '<record></record>', 'insert')
    assert 'LEGACY_ROBOTUPLOAD_URL' in str(excinfo.value)

    httpretty.HTTPretty.allow_net_connect = True


@pytest.mark.httpretty
def test_make_robotupload_marcxml_handles_utf8():
    httpretty.HTTPretty.allow_net_connect = False
    httpretty.register_uri(
        httpretty.POST, 'http://localhost:5000/batchuploader/robotupload/insert')

    snippet = (
        '<record>'
        '  <datafield tag="700" ind1=" " ind2=" ">'
        '    <subfield code="a">André, M.</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1503367

    make_robotupload_marcxml('http://localhost:5000', snippet, 'insert')

    httpretty.HTTPretty.allow_net_connect = True
