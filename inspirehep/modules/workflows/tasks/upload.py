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
from pprint import pformat


from flask import url_for

from invenio_db import db

from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.records.api import InspireRecord

from ..utils import with_debug_logging


@with_debug_logging
def store_record(obj, *args, **kwargs):
    """Create and index new record in main record space."""
    obj.log.debug('Storing record: \n%s', pformat(obj.data))

    assert "$schema" in obj.data, "No $schema attribute found!"

    # Create record
    # FIXME: Do some preprocessing of obj.data before creating a record so that
    # we're sure that the schema will be validated without touching the full
    # holdingpen stack.
    record = InspireRecord.create(obj.data, id_=None)

    for key in obj.files.keys:
        with open(os.path.realpath(obj.files[key].file.uri)) as stream:
            record.files[key] = stream
            for attachment in itertools.chain(record.get('documents', []), record.get('figures', [])):
                if key == attachment['key']:
                    attachment['url'] = '/api/files/{bucket}/{key}'.format(bucket=record.files[key].bucket_id, key=key)
                    break

    # Create persistent identifier.
    created_pid = inspire_recid_minter(str(record.id), record).pid_value

    # Commit any changes to record
    record.commit()

    # Commit to DB before indexing
    db.session.commit()

    obj.data['control_number'] = created_pid


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
