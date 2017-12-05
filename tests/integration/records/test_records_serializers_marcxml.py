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


def test_marcxml_serializer_serialize(api_client):
    response = api_client.get(
        '/literature/701585',
        headers={'Accept': 'application/marcxml+xml'},
    )

    assert response.status_code == 200

    expected = b'<controlfield tag="001">701585</controlfield>'
    result = response.data

    assert expected in result


def test_marcxml_serializer_serialize_results(api_client):
    response = api_client.get(
        '/literature/?q=title collider',
        headers={'Accept': 'application/marcxml+xml'},
    )

    assert response.status_code == 200

    expected_701585 = b'<controlfield tag="001">701585</controlfield>'
    expected_1373790 = b'<controlfield tag="001">1373790</controlfield>'
    result = response.data

    assert expected_701585 in result
    assert expected_1373790 in result
