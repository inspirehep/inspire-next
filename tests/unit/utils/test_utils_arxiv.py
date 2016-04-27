# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for arXiv utilities."""

import pytest

from inspirehep.utils.arxiv import get_clean_arXiv_id


@pytest.fixture
def arxiv_record():
    return {
        "arxiv_eprints": [
            {
                "value": "arXiv:1002.2647",
            }
        ]
    }


@pytest.fixture
def arxiv_record_old():
    return {
        "arxiv_eprints": [
            {
                "value": "physics/0112006",
            }
        ]
    }


@pytest.fixture
def arxiv_record_oai():
    return {
        "arxiv_eprints": [
            {
                "value": "oai:arXiv.org:physics/0112006",
            }
        ]
    }


def test_arxiv_id_getter(arxiv_record, arxiv_record_old, arxiv_record_oai):
    """Test retrieval of arXiv ID."""
    assert "1002.2647" == get_clean_arXiv_id(arxiv_record)
    assert "physics/0112006" == get_clean_arXiv_id(arxiv_record_old)
    assert "physics/0112006" == get_clean_arXiv_id(arxiv_record_oai)
    assert get_clean_arXiv_id({}) is None
