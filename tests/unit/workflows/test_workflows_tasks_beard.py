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

import mock

from inspirehep.modules.workflows.tasks.beard import get_beard_url


@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.current_app.config',
    {'BEARD_API_URL': 'https://beard.inspirehep.net'})
def test_get_beard_url_from_configuration():
    expected = 'https://beard.inspirehep.net/predictor/coreness'
    result = get_beard_url()

    assert expected == result


@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.current_app.config',
    {'BEARD_API_URL': ''})
def test_get_beard_url_returns_none_when_not_in_configuration():
    assert get_beard_url() is None
