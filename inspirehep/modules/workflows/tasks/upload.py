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

"""Tasks related to record uploading."""

from __future__ import absolute_import, division, print_function

from flask import url_for

from invenio_db import db

from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.records.api import InspireRecord

from ..utils import with_debug_logging


@with_debug_logging
def store_record(obj, eng):
    """Insert or replace a record."""
    is_update = obj.extra_data.get('is-update')
    if is_update:
        record = InspireRecord.get_record(obj.extra_data['head_uuid'])
        record.clear()
        record.update(obj.data, files_src_records=[obj])

    else:
        record = InspireRecord.create(obj.data, id_=None)
        # Create persistent identifier.
        created_pid = inspire_recid_minter(str(record.id), record).pid_value
        # Now that we have a recid, we can properly download the documents
        record.download_documents_and_figures(src_records=[obj])

        obj.data['control_number'] = created_pid
        # store head_uuid to store the root later
        obj.extra_data['head_uuid'] = str(record.id)

    record.commit()
    obj.save()
    db.session.commit()


@with_debug_logging
def set_schema(obj, eng):
    """Make sure schema is set properly and resolve it."""
    if '$schema' not in obj.data:
        obj.data['$schema'] = "{data_type}.json".format(
            data_type=obj.data_type or eng.workflow_definition.data_type
        )
        obj.log.debug('Schema set to %s', obj.data['$schema'])
    else:
        obj.log.debug('Schema already there')

    if not obj.data['$schema'].startswith('http'):
        old_schema = obj.data['$schema']
        obj.data['$schema'] = url_for(
            'invenio_jsonschemas.get_schema',
            schema_path="records/{0}".format(obj.data['$schema'])
        )
        obj.log.debug(
            'Schema changed to %s from %s', obj.data['$schema'], old_schema
        )
    else:
        obj.log.debug('Schema already is url')

    obj.log.debug('Final schema %s', obj.data['$schema'])
