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

from flask import current_app
from mock import patch

from inspirehep.modules.hal.core.sword import _new_connection


def test_new_connection_is_secure_by_default():
    connection = _new_connection()

    assert not connection.h.h.disable_ssl_certificate_validation


def test_new_connection_can_be_configured_to_be_insecure():
    config = {'HAL_IGNORE_CERTIFICATES': True}

    with patch.dict(current_app.config, config):
        connection = _new_connection()

        assert connection.h.h.disable_ssl_certificate_validation
