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

"""Tests for HEP DoJSON receivers."""

import pytest

from inspirehep.dojson.hep.receivers import earliest_date


@pytest.fixture
def full_record():
    """."""
    return {
        "preprint_date": "2014-05-29",
        "arxiv_eprints": [
            {
                "categories": ["hep-ex"],
                "value": "arXiv:1405.7570"
            }
        ],
        "publication_info": [
            {
                "journal_issue": "9",
                "journal_recid": 1212905,
                "journal_title": "Eur.Phys.J.",
                "journal_volume": "C74",
                "page_artid": "3036",
                "year": 2014
            }
        ],
        "creation_modification_date": [
            {
                "creation_date": "2015-11-04",
                "modification_date": "2014-05-30"
            }
        ],
        "imprints": [{"date": "2014-09-26"}],
        "thesis": [
            {
                "curated_relation": "false",
                "date": "2008",
                "degree_type":
                "PhD"
            }
        ]

    }


@pytest.fixture
def pub_info(full_record):
    """."""
    return {
        "publication_info": full_record["publication_info"]
    }


@pytest.fixture
def creation_modification_date(full_record):
    """."""
    return {
        "creation_modification_date": full_record["creation_modification_date"]
    }


@pytest.fixture
def imprints(full_record):
    """."""
    return {
        "imprints": full_record["imprints"]
    }


@pytest.fixture
def thesis(full_record):
    """."""
    return {
        "thesis": full_record["thesis"]
    }


def test_earliest_date(full_record, pub_info, creation_modification_date,
                       imprints, thesis):
    """Test earliest_date record enhancer."""
    earliest_date(full_record)
    earliest_date(pub_info)
    earliest_date(creation_modification_date)
    earliest_date(imprints)
    earliest_date(thesis)
    assert full_record['earliest_date'] == '2008'
    assert pub_info['earliest_date'] == '2014'
    assert creation_modification_date['earliest_date'] == '2015-11-04'
    assert imprints['earliest_date'] == '2014-09-26'
    assert thesis['earliest_date'] == '2008'
