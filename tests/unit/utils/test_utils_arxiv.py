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

from inspirehep.utils.arxiv import get_clean_arXiv_id


def test_get_clean_arXiv_id_returns_none_when_no_arxiv_eprints():
    assert get_clean_arXiv_id({}) is None


def test_get_clean_arXiv_id_from_arxiv_eprints_using_new_style():
    record = {
        'arxiv_eprints': [
            {'value': 'arxiv:1002.2647'},
        ],
    }

    expected = '1002.2647'
    result = get_clean_arXiv_id(record)

    assert expected == result


def test_get_clean_arXiv_id_from_arxiv_eprints_using_old_style():
    record = {
        'arxiv_eprints': [
            {'value': 'physics/0112006'},
        ],
    }

    expected = 'physics/0112006'
    result = get_clean_arXiv_id(record)

    assert expected == result


def test_get_clean_arXiv_id_from_arxiv_eprints_with_oai_prefix():
    record = {
        'arxiv_eprints': [
            {'value': 'oai:arXiv.org:physics/0112006'},
        ],
    }

    expected = 'physics/0112006'
    result = get_clean_arXiv_id(record)

    assert expected == result


def test_get_clean_arXiv_id_from_arxiv_eprints_selects_last():
    record = {
        'arxiv_eprints': [
            {'value': 'oai:arXiv.org:0801.4782'},
            {'value': 'oai:arXiv.org:0805.1410'},
        ],
    }

    expected = '0805.1410'
    result = get_clean_arXiv_id(record)

    assert expected == result
