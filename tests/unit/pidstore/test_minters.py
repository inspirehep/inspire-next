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

from mock import Mock, patch

from inspirehep.modules.pidstore import minters


def test_mint_pids_all():
    minter1 = Mock()
    minter2 = Mock()

    with patch('inspirehep.modules.pidstore.minters.MINTERS',
               (minter1, minter2)):
        record_uuid = Mock()
        data = Mock()
        minters.mint_pids(record_uuid, data)

    minter1.assert_called_once_with(record_uuid, data)
    minter2.assert_called_once_with(record_uuid, data)


def test_mint_pids_collection():
    minter1 = Mock()
    minter2 = Mock()

    record_uuid = Mock()
    data = Mock()
    minters.mint_pids(record_uuid, data, (minter1, minter2))

    minter1.assert_called_once_with(record_uuid, data)
    minter2.assert_called_once_with(record_uuid, data)
