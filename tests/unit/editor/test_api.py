# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2020 CERN.
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
from mock import patch
from flask import current_app

from inspirehep.modules.editor.api import _replace_xrootd_with_http


def test_replace_xrootd_with_http():
    eos_prefix = "root://eospublic.cern.ch"

    config = {
        "EOS_XROOTD_PREFIX": eos_prefix,
        "EOS_HTTP_PREFIX": "http://example.com",
    }
    expected_result = 'http://example.com//eos/workspace/tmp/file.pdf'

    with patch.dict(current_app.config, config):
        path = '{}//eos/workspace/tmp/file.pdf'.format(eos_prefix)
        result = _replace_xrootd_with_http(path)

    assert expected_result == result
