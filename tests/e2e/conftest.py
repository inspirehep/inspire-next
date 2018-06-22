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
import pytest
import time

from inspirehep.testlib.api import InspireApiClient
from inspirehep.testlib.api.mitm_client import MITMClient


@pytest.fixture(autouse=True, scope='function')
def init_environment(inspire_client):
    inspire_client.e2e.init_db()
    inspire_client.e2e.init_es()
    inspire_client.e2e.init_fixtures()
    # refresh login session, giving a bit of time
    time.sleep(1)
    inspire_client.login_local()


@pytest.fixture
def inspire_client():
    """Share the same client to reuse the same session"""
    # INSPIRE_API_URL is set by k8s when running the test in Jenkins
    inspire_url = os.environ.get('INSPIRE_API_URL', 'http://test-web-e2e.local:5000')
    return InspireApiClient(base_url=inspire_url)


@pytest.fixture
def mitm_client():
    mitmproxy_url = os.environ.get('MITMPROXY_HOST', 'http://mitm-manager.local')
    return MITMClient(mitmproxy_url)
