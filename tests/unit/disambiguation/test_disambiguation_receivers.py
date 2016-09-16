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

"""Test *helpers* (_method_name(foo, bar):) from receivers.py"""

from __future__ import absolute_import, division, print_function

from inspirehep.modules.disambiguation.receivers import (
    _needs_beard_reprocessing,
)


def test_check_if_record_eligible_method():
    """Check if the method will correctly qualify updates to authors."""
    base_author = [{
        "uuid": "819695a8-6aef-4ce2-979e-20eb0eccfd8c",
        "affiliations": [{
            "record": {
                "$ref": "http://localhost:5000/api/institutions/902770"
            },
            "recid": 902770,
            "value": "DESY"
        }],
        "full_name": "Schörner-Sadenius, Thomas",
    }]

    author_new_affiliation = [{
        "uuid": "819695a8-6aef-4ce2-979e-20eb0eccfd8c",
        "affiliations": [{
            "value": "CERN"
        }],
        "full_name": "Schörner-Sadenius, Thomas",
    }]

    author_new_name = [{
        "uuid": "819695a8-6aef-4ce2-979e-20eb0eccfd8c",
        "affiliations": [{
            "record": {
                "$ref": "http://localhost:5000/api/institutions/902770"
            },
            "recid": 902770,
            "value": "DESY"
        }],
        "full_name": "Schörner-Sadenius, T",
    }]

    new_author = [{
        "uuid": "819695a8-6aef-4ce2-979e-20eb0eccfd8c",
        "affiliations": [{
            "record": {
                "$ref": "http://localhost:5000/api/institutions/902770"
            },
            "recid": 902770,
            "value": "DESY"
        }],
        "full_name": "Schörner-Sadenius, Thomas",
    }, {
        "uuid": "e24251bc-e75b-45ef-9e71-7181ed3a7fb5",
        "affiliations": [{
            "value": "CERN"
        }],
        "full_name": "Grzegorz Jacenków"
    }]

    assert not _needs_beard_reprocessing(base_author, base_author)
    assert _needs_beard_reprocessing(base_author, author_new_affiliation)
    assert _needs_beard_reprocessing(base_author, author_new_name)
    assert _needs_beard_reprocessing(base_author, new_author)
