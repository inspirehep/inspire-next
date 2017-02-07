# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

import pytest

from inspirehep.modules.api.utils import (
    get_date,
    get_document_type,
    get_id,
    get_subject,
    is_collaboration,
    is_core,
    is_selfcite,
)


def test_get_date():
    record = {'earliest_date': '1993-02-02'}

    expected = '1993-02-02'
    result = get_date(record)

    assert expected == result


def test_get_date_raises_when_no_earliest_date():
    record = {}

    with pytest.raises(KeyError):
        get_date(record)


def test_get_document_type():
    record = {
        'facet_inspire_doc_type': [
            'peer reviewed',
        ],
    }

    expected = 'peer reviewed'
    result = get_document_type(record)

    assert expected == result


def test_get_document_type_returns_none_when_facet_inspire_doc_type_is_empty():
    record = {'facet_inspire_doc_type': []}

    assert get_document_type(record) is None


def test_get_document_type_returns_none_when_no_facet_inspire_doc_type():
    record = {}

    assert get_document_type(record) is None


def test_get_id():
    record = {'control_number': 4328}

    expected = 4328
    result = get_id(record)

    assert expected == result


def test_get_id_raises_when_no_control_number():
    record = {}

    with pytest.raises(KeyError):
        assert get_id(record)


def test_get_subject():
    record = {
        'inspire_categories': [
            {'term': 'Phenomenology-HEP'},
        ],
    }

    expected = 'Phenomenology-HEP'
    result = get_subject(record)

    assert expected == result


def test_get_subject_selects_first():
    record = {
        'inspire_categories': [
            {'term': 'Experiments-HEP'},
            {'term': 'Phenomenology-HEP'},
        ],
    }

    expected = 'Experiments-HEP'
    result = get_subject(record)

    assert expected == result


def test_is_collaboration():
    record = {
        'collaborations': [
            {'value': 'CMS'},
        ],
    }

    assert is_collaboration(record)


def test_is_collaboration_returns_false_when_no_collaboration():
    record = {}

    assert not is_collaboration(record)


def test_is_core():
    record = {'core': True}

    assert is_core(record)


def test_is_core_returns_false_when_no_core():
    record = {}

    assert not is_core(record)


def test_is_core_returns_false_when_core_is_false():
    record = {'core': False}

    assert not is_core(record)


def test_is_selfcite_returns_true_when_at_least_one_author_recid_is_in_common():
    citee = {
        'authors': [
            {'recid': '2'},
            {'recid': '1'},
        ],
    }
    citer = {
        'authors': [
            {'recid': '1'},
        ],
    }

    assert is_selfcite(citee, citer)


def test_is_selfcite_returns_false_when_no_authors_recids_are_in_common():
    citee = {
        'authors': [
            {'recid': '1'},
        ],
    }
    citer = {
        'authors': [
            {'recid': '2'},
        ],
    }

    assert not is_selfcite(citee, citer)
