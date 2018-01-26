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

import uuid
from mock import patch

import pytest

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.migrator.models import InspireProdRecords
from inspirehep.modules.migrator.tasks import _build_recid_to_uuid_map, migrate_and_insert_record


def test_build_recid_to_uuid_map_numeric_pid_allowed_for_lit_and_con(isolated_app):
    pid1 = PersistentIdentifier.create(pid_type='lit', pid_value='123',
                                       object_type='rec', object_uuid=uuid.uuid4())
    pid2 = PersistentIdentifier.create(pid_type='con', pid_value='1234',
                                       object_type='rec', object_uuid=uuid.uuid4())
    citations_lookup = {
        pid1.pid_value: 5,
        pid2.pid_value: 6,
    }
    result = _build_recid_to_uuid_map(citations_lookup)
    assert result.keys().sort() == [pid1.object_uuid, pid2.object_uuid].sort()


def test_build_recid_to_uuid_map_numeric_pid_breaks_for_lit(isolated_app):
    pid1 = PersistentIdentifier.create(pid_type='lit', pid_value='abcdef',
                                       object_type='rec', object_uuid=uuid.uuid4())
    citations_lookup = {
        pid1.pid_value: 5,
    }
    with pytest.raises(ValueError):
        _build_recid_to_uuid_map(citations_lookup)


def test_build_recid_to_uuid_map_ignored_types(isolated_app):
    citations_lookup = {}
    for type in ('urn', 'tex', 'cust'):
        pid = PersistentIdentifier.create(
            pid_type=type, pid_value='abcd', object_type='rec',
            object_uuid=uuid.uuid4())
        citations_lookup[pid.pid_value] = 6
    result = _build_recid_to_uuid_map(citations_lookup)
    assert result == {}


@patch('inspirehep.modules.migrator.tasks.LOGGER')
def test_migrate_and_insert_record_valid_record(mock_logger, isolated_app):
    raw_record = (
        '<record>'
        '  <controlfield tag="001">12345</controlfield>'
        '  <datafield tag="245" ind1=" " ind2=" ">'
        '    <subfield code="a">On the validity of INSPIRE records</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    migrate_and_insert_record(raw_record)

    prod_record = InspireProdRecords.query.filter(InspireProdRecords.recid == 12345).one()
    assert prod_record.valid is True
    assert prod_record.marcxml == raw_record

    assert not mock_logger.error.called
    assert not mock_logger.exception.called


@patch('inspirehep.modules.migrator.tasks.LOGGER')
def test_migrate_and_insert_record_dojson_error(mock_logger, isolated_app):
    raw_record = (
        '<record>'
        '  <controlfield tag="001">12345</controlfield>'
        '  <datafield tag="260" ind1=" " ind2=" ">'
        '    <subfield code="c">Definitely not a date</subfield>'
        '  </datafield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    migrate_and_insert_record(raw_record)

    prod_record = InspireProdRecords.query.filter(InspireProdRecords.recid == 12345).one()
    assert prod_record.valid is False
    assert prod_record.marcxml == raw_record

    assert not mock_logger.error.called
    mock_logger.exception.assert_called_once_with('Migrator DoJSON Error')


@patch('inspirehep.modules.migrator.tasks.LOGGER')
def test_migrate_and_insert_record_invalid_record(mock_logger, isolated_app):
    raw_record = (
        '<record>'
        '  <controlfield tag="001">12345</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    migrate_and_insert_record(raw_record)

    prod_record = InspireProdRecords.query.filter(InspireProdRecords.recid == 12345).one()
    assert prod_record.valid is False
    assert prod_record.marcxml == raw_record

    assert mock_logger.error.called
    assert not mock_logger.exception.called


@patch('inspirehep.modules.migrator.tasks.record_insert_or_replace', side_effect=Exception())
@patch('inspirehep.modules.migrator.tasks.LOGGER')
def test_migrate_and_insert_record_other_exception(mock_logger, isolated_app):
    raw_record = (
        '<record>'
        '  <controlfield tag="001">12345</controlfield>'
        '  <datafield tag="980" ind1=" " ind2=" ">'
        '    <subfield code="a">HEP</subfield>'
        '  </datafield>'
        '</record>'
    )

    migrate_and_insert_record(raw_record)

    prod_record = InspireProdRecords.query.filter(InspireProdRecords.recid == 12345).one()
    assert prod_record.valid is False
    assert prod_record.marcxml == raw_record

    assert not mock_logger.error.called
    mock_logger.exception.assert_called_once_with('Migrator Record Insert Error')
