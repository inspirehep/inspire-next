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

from inspirehep.modules.literaturesuggest.normalizers import (
    split_page_range_article_id,
)


class DummyObj(object):
    pass


def test_split_page_range_article_id():
    obj = DummyObj()
    formdata = {'page_range_article_id': '789-890'}

    expected = {
        'artid': None,
        'page_end': '890',
        'page_range_article_id': '789-890',
        'page_start': '789',
    }
    result = split_page_range_article_id(obj, formdata)

    assert expected == result
