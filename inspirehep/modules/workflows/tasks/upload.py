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

import os
import itertools

from flask import url_for

from invenio_db import db

from inspirehep.utils.record_getter import get_db_record
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
        record.update(obj.data)

    else:
        record = InspireRecord.create(obj.data, id_=None)
        # Create persistent identifier.
        created_pid = inspire_recid_minter(str(record.id), record).pid_value
        obj.data['control_number'] = created_pid
        # store head_uuid to store the root later
        obj.extra_data['head_uuid'] = str(record.id)

    attach_files_to_record_from_workflow(obj, record)
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


def attach_files_to_record_from_workflow(workflow_obj, record):
    for file_id in workflow_obj.files.keys:
        with open(os.path.realpath(workflow_obj.files[file_id].file.uri)) as stream:
            record.attach_file(file_id, stream)


def are_files_consistent(record_id):
    """Check the consistency between documents and figures in the record
    metadata and the files attached to the record itself.

    Params:
        record_id(int): the control_number of the record
        other_extensions(string): file extension used to make this check
            aware of other types of files other than `documents` and `figures`.

    Return:
        bool: True if attached files correspond to the files in `documents`
            and `figures`, (and eventually other types of files specified in
            `other_extensions`) otherwise False.
    """
    record = get_db_record('lit', record_id)

    docs_and_figs = [
        doc['key'] for doc in itertools.chain(
            record.get('documents', []), record.get('figures', [])
        )]

    for file_name in docs_and_figs:
        if file_name not in record.files.keys:
            return False

    for file_name in docs_and_figs:
        if not file_name.startswith("{}_".format(record_id)):
            return False

    return True
