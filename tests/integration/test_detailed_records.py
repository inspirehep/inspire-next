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

from invenio_records.models import RecordMetadata

from inspirehep.modules.migrator.models import LegacyRecordsMirror


def test_all_records_were_loaded(app):
    records = [record.json for record in RecordMetadata.query.all()]

    expected = 43
    result = len(records)

    assert expected == result


def test_all_records_are_valid(app):
    invalid = LegacyRecordsMirror.query.filter(LegacyRecordsMirror.valid is False).values(LegacyRecordsMirror.recid)
    recids = [el[0] for el in invalid]

    assert recids == []
