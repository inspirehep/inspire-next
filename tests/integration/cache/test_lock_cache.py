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

"""Test lock cache."""

from __future__ import absolute_import, division, print_function

from inspirehep.modules.cache import lock_cache


def test_lock_cache_creation(app):
    """Test set key."""
    lock_cache.set('Defenders', 'Jessica Jones')
    expected = 'Jessica Jones'
    result = lock_cache.get('Defenders')

    assert expected == result

    lock_cache.set('Defenders', 'Jessica Jones, Luke Cage')
    expected = 'Jessica Jones, Luke Cage'
    result = lock_cache.get('Defenders')

    assert expected == result


def test_lock_cache_deletion():
    """Test delete key."""
    lock_cache.set('Defenders', 'Jessica Jones')
    expected = 'Jessica Jones'
    result = lock_cache.get('Defenders')

    assert expected == result

    lock_cache.delete('Defenders')
    result = lock_cache.get('Defenders')

    assert result is None
