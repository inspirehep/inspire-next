# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

from inspirehep.modules.orcid.models import InspireOrcidPutCodes
from invenio_db import db


@pytest.fixture(scope='function')
def setup_and_teardown_db():
    with db.session.begin_nested():
        entry = InspireOrcidPutCodes()
        entry.recid = 111111
        entry.put_code = 222222
        with db.session.begin_nested():
            db.session.add(entry)

    yield

    InspireOrcidPutCodes.query.filter_by(recid=123456).delete()
    InspireOrcidPutCodes.query.filter_by(recid=111111).delete()


def test_set_put_code_new(setup_and_teardown_db):
    InspireOrcidPutCodes.set_put_code(recid=123456, put_code=456789)

    expected = 456789
    result = InspireOrcidPutCodes.query.filter_by(recid=123456).one().put_code

    assert expected == result


def test_set_put_code_existing(setup_and_teardown_db):
    InspireOrcidPutCodes.set_put_code(recid=111111, put_code=456789)

    expected = 456789
    result = InspireOrcidPutCodes.query.filter_by(recid=111111).one().put_code

    assert expected == result


def test_get_put_code(setup_and_teardown_db):
    expected = 222222
    result = InspireOrcidPutCodes.get_put_code(111111)

    assert expected == result
