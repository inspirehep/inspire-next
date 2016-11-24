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

import pytest

from elasticsearch import NotFoundError

from invenio_records.api import Record
from invenio_records.signals import before_record_update

from inspirehep.modules.records.receivers import (
    check_if_record_is_going_to_be_deleted
)
from inspirehep.modules.search import LiteratureSearch


def test_receive_after_model_commit(app):
    """Test if records are correctly synced with ElasticSearch."""
    before_record_update.disconnect(check_if_record_is_going_to_be_deleted)
    json = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "Hello": "World"
    }
    record = Record.create(json)
    search = LiteratureSearch()
    es_record = search.get_source(record.id)
    assert es_record["Hello"] == "World"

    record["Hello"] = "INSPIRE"
    record.commit()
    es_record = search.get_source(record.id)
    assert es_record["Hello"] == "INSPIRE"

    record.delete(force=True)
    with pytest.raises(NotFoundError):
        es_record = search.get_source(record.id)
    before_record_update.connect(check_if_record_is_going_to_be_deleted)
