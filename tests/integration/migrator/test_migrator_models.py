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

from inspirehep.modules.migrator.models import InspireProdRecords


def test_inspire_prod_records_from_marcxml():
    raw_record = '''
        <record>
          <controlfield tag="001">1591551</controlfield>
          <controlfield tag="005">20171011194718.0</controlfield>
          <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Chetyrkin, K.G.</subfield>
          </datafield>
        </record>
        '''

    record = InspireProdRecords.from_marcxml(raw_record)

    assert record.recid == 1591551
    assert record.marcxml == raw_record
    assert record.valid is None
    assert record.error is None


def test_inspire_prod_records_from_marcxml_raises_for_invalid_recid():
    raw_record = '''
        <record>
          <controlfield tag="001">foo</controlfield>
          <controlfield tag="005">20171011194718.0</controlfield>
          <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Chetyrkin, K.G.</subfield>
          </datafield>
        </record>
        '''

    with pytest.raises(ValueError):
        InspireProdRecords.from_marcxml(raw_record)


def test_inspire_prod_records_error():
    record = InspireProdRecords(recid='12345')
    error = ValueError(u'This is an error with ùnicode')

    record.error = error

    assert record.error == u'ValueError: This is an error with ùnicode'
