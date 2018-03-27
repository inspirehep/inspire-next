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

from invenio_db import db

from inspirehep.modules.pidstore.utils import get_pid_type_from_schema
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.utils import with_debug_logging
from inspirehep.utils.record_getter import get_db_record
from inspirehep.utils.schema import ensure_valid_schema


@with_debug_logging
def store_record(obj, eng):
    """Insert or replace a record."""
    def _get_updated_record(obj):
        """TODO: use only head_uuid once we have the merger."""
        if 'head_uuid' in obj.extra_data:
            updated_record = InspireRecord.get_record(
                obj.extra_data['head_uuid'],
            )
        else:
            pid_type = get_pid_type_from_schema(obj.data['$schema'])
            updated_record_id = obj.extra_data['matches']['approved']
            updated_record = get_db_record(pid_type, updated_record_id)

        return updated_record

    is_update = obj.extra_data.get('is-update')
    if is_update:
        record = _get_updated_record(obj)
        obj.data['control_number'] = record['control_number']
        record.clear()
        record.update(obj.data, files_src_records=[obj])

    else:
        # Skip the files to avoid issues in case the record has already pid
        # TODO: remove the skip files once labs becomes master
        record = InspireRecord.create(obj.data, id_=None, skip_files=True)
        # Create persistent identifier.
        # Now that we have a recid, we can properly download the documents
        record.download_documents_and_figures(src_records=[obj])

        obj.data['control_number'] = record['control_number']
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

    old_schema = obj.data['$schema']
    ensure_valid_schema(obj.data)
    if obj.data['$schema'] != old_schema:
        obj.log.debug(
            'Schema changed to %s from %s', obj.data['$schema'], old_schema
        )
    else:
        obj.log.debug('Schema already is url')

    obj.log.debug('Final schema %s', obj.data['$schema'])
