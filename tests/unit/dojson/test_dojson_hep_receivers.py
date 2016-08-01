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

from invenio_records.api import Record

from inspirehep.dojson.hep.receivers import earliest_date


def test_earliest_date_from_preprint_date():
    with_preprint_date = Record({'preprint_date': '2014-05-29'})
    earliest_date(with_preprint_date)

    expected = '2014-05-29'
    result = with_preprint_date['earliest_date']

    assert expected == result


def test_earliest_date_from_thesis_date():
    with_thesis_date = Record({
        'thesis': {'date': '2008'}
    })
    earliest_date(with_thesis_date)

    expected = '2008'
    result = with_thesis_date['earliest_date']

    assert expected == result


def test_earliest_date_from_thesis_defense_date():
    with_thesis_defense_date = Record({
        'thesis': {'defense_date': '2012-06-01'}
    })
    earliest_date(with_thesis_defense_date)

    expected = '2012-06-01'
    result = with_thesis_defense_date['earliest_date']

    assert expected == result


def test_earliest_date_from_publication_info_year():
    with_publication_info_year = Record({
        'publication_info': [
            {'year': '2014'}
        ]
    })
    earliest_date(with_publication_info_year)

    expected = '2014'
    result = with_publication_info_year['earliest_date']

    assert expected == result


def test_earliest_date_from_creation_modification_date_creation_date():
    with_creation_modification_date_creation_date = Record({
        'creation_modification_date': [
            {'creation_date': '2015-11-04'}
        ]
    })
    earliest_date(with_creation_modification_date_creation_date)

    expected = '2015-11-04'
    result = with_creation_modification_date_creation_date['earliest_date']

    assert expected == result


def test_earliest_date_from_imprints_date():
    with_imprints_date = Record({
        'imprints': [
            {'date': '2014-09-26'}
        ]
    })
    earliest_date(with_imprints_date)

    expected = '2014-09-26'
    result = with_imprints_date['earliest_date']

    assert expected == result
