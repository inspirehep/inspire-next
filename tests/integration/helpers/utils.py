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

import re
from contextlib import contextmanager

import requests_mock

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, RecordIdentifier
from invenio_search import current_search_client as es

from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.utils.record_getter import get_db_record


def _delete_record(pid_type, pid_value):
    get_db_record(pid_type, pid_value)._delete(force=True)

    pid = PersistentIdentifier.get(pid_type, pid_value)
    PersistentIdentifier.delete(pid)

    recpid = RecordIdentifier.query.filter_by(recid=pid_value).one_or_none()
    if recpid:
        db.session.delete(recpid)

    object_uuid = pid.object_uuid
    PersistentIdentifier.query.filter(
        object_uuid == PersistentIdentifier.object_uuid).delete()

    db.session.commit()


@contextmanager
def mock_addresses(addresses, mocked_local=False):
    with requests_mock.Mocker() as requests_mocker:
        if not mocked_local:
            requests_mocker.register_uri(
                requests_mock.ANY,
                re.compile('.*(indexer|localhost).*'),
                real_http=True,
            )

        for address in addresses:
            requests_mocker.register_uri(**address)

        yield


def _create_record(record_json):
    with db.session.begin_nested():
        record_insert_or_replace(record_json)

    db.session.commit()
    es.indices.refresh()

    return record_json
