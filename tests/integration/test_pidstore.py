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
import mock
import pytest

from inspirehep.modules.pidstore.providers import InspireRecordIdProvider


@pytest.mark.httpretty
def test_getting_next_recid_from_legacy(app):
    extra_config = {
        'LEGACY_PID_PROVIDER': 'http://server/batchuploader/allocaterecord',
    }

    with app.app_context():
        with mock.patch.dict(app.config, extra_config):
            httpretty.register_uri(
                httpretty.GET,
                'http://server/batchuploader/allocaterecord',
                content_type='application/json',
                body='3141592',
                status=200,
            )

            args = dict(
                object_type='rec',
                object_uuid='7753a30b-4c4b-469c-8d8d-d5020069b3ab',
                pid_type='lit'
            )
            provider = InspireRecordIdProvider.create(**args)

            assert str(provider.pid.pid_value) == "3141592"
