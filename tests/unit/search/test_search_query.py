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

import pytest
from inspirehep.modules.search.search_factory import inspire_search_factory
from invenio_records_rest.errors import InvalidQueryRESTError
from mock import Mock, patch


@pytest.mark.xfail(raises=InvalidQueryRESTError)
@patch('inspirehep.modules.search.search_factory.request')
def test_inspire_search_factory(mocked_request):
    mocked_request.values.get.return_value = u'φοο'

    search_mock = Mock()
    search_mock.query.side_effect = SyntaxError
    search_mock.to_dict.return_value = None

    mocked_self = Mock()

    assert inspire_search_factory(mocked_self, search_mock)
