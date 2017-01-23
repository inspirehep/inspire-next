# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from inspirehep.modules.authors.views.holdingpen import (
    convert_for_form,
    get_inspire_url,
)
from inspirehep.modules.records.api import InspireRecord


def test_convert_for_form_without_name_urls_fc_positions_advisors_and_ids():
    without_name_urls_fc_positions_advisors_and_ids = InspireRecord({})
    convert_for_form(without_name_urls_fc_positions_advisors_and_ids)

    assert InspireRecord({}) == without_name_urls_fc_positions_advisors_and_ids


def test_convert_for_form_public_emails():
    current_and_old_emails = {
        'positions': [
            {
                "emails": [
                    "michael.abbott@uct.ac.za"
                ]
            },
            {
                "emails": [
                    "abbott@theory.tifr.res.in"
                ]
            },
            {
                "old_emails": [
                    "abbott@het.brown.edu"
                ]
            }
        ]
    }
    convert_for_form(current_and_old_emails)

    expected = [
        {
          "email": "michael.abbott@uct.ac.za",
          "original_email": "michael.abbott@uct.ac.za"
        },
        {
          "email": "abbott@theory.tifr.res.in",
          "original_email": "abbott@theory.tifr.res.in"
        }
    ]

    assert expected == current_and_old_emails['public_emails']


# TODO: test convert_for_form


def test_get_inspire_url_with_bai():
    with_bai = InspireRecord({'bai': 'TODO'})

    expected = 'http://inspirehep.net/author/profile/TODO'
    result = get_inspire_url(with_bai)

    assert expected == result


def test_get_inspire_url_with_control_number():
    with_recid = InspireRecord({'control_number': 'TODO'})

    expected = 'http://inspirehep.net/record/TODO'
    result = get_inspire_url(with_recid)

    assert expected == result


def test_get_inspire_url_without_recid_or_bai():
    without_recid_or_bai = InspireRecord({})

    expected = 'http://inspirehep.net/hepnames'
    result = get_inspire_url(without_recid_or_bai)

    assert expected == result
