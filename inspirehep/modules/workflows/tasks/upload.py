# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tasks related to record uploading."""

from __future__ import absolute_import, print_function

from flask import url_for

from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records import Record

from inspirehep.modules.pidstore.minters import inspire_recid_minter


def store_record(obj, *args, **kwargs):
    """Create and index new record in main record space."""
    if '$schema' in obj.data:
        obj.data['$schema'] = url_for(
            'invenio_jsonschemas.get_schema',
            schema_path="records/{0}".format(obj.data['$schema'])
        )
    # Create record
    rec_uuid = str(Record.create(obj.data, id_=None).id)

    # Create persistent identifier.
    pid = inspire_recid_minter(rec_uuid, obj.data)
    db.session.commit()

    # Index record
    indexer = RecordIndexer()
    indexer.index_by_id(pid.object_uuid)
