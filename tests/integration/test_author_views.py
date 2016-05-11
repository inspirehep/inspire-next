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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

import json


def test_author_publications_is_there(app):
    with app.test_client() as client:
        assert client.get(
            '/author/publications?recid=984519').status_code == 200


def test_author_publications_returns_the_right_data(app):
    with app.test_client() as client:
        response = json.loads(
            client.get('/author/publications?recid=984519').data)

        # FIXME: Asserts should be more specific.
        assert len(response['collaborations']) == 4
        assert len(response['keywords']) == 218
        assert len(response['publications']) == 30
