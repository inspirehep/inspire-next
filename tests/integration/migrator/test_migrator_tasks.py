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
import uuid

from inspirehep.modules.migrator.tasks import _build_recid_to_uuid_map
from invenio_pidstore.models import PersistentIdentifier


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
