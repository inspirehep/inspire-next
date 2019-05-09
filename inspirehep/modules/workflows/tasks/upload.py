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

import requests
from flask import current_app
from invenio_workflows.errors import WorkflowsError

from inspire_schemas.readers import LiteratureReader
from invenio_db import db

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.workflows.models import WorkflowsRecordSources
from inspirehep.modules.workflows.utils import (
    get_source_for_root,
    with_debug_logging,
)
from inspirehep.utils.schema import ensure_valid_schema


@with_debug_logging
def store_record(obj, eng):
    """Insert or replace a record."""
    is_update = obj.extra_data.get('is-update')
    is_authors = eng.workflow_definition.data_type == 'authors'
    if not current_app.config.get("ENABLE_INSPIREHEP_REMOTE_RECORD_MANAGEMENT"):
        with db.session.begin_nested():
            if is_update:
                if not is_authors and not current_app.config.get('FEATURE_FLAG_ENABLE_MERGER', False):
                    obj.log.info(
                        'skipping update record, feature flag ``FEATURE_FLAG_ENABLE_MERGER`` is disabled.'
                    )
                    return

                record = InspireRecord.get_record(obj.extra_data['head_uuid'])
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
    else:
        store_record_inspirehep_api(obj, eng, is_update, is_authors)


@with_debug_logging
def store_record_inspirehep_api(obj, eng, is_update, is_authors):
    """Saves record through inspirehep api by posting/pushing record to proper endpoint
     in inspirehep"""
    headers = {
        "content-type": "application/json",
        "Authorization": "Bearer {token}".format(
            token=current_app.config['AUTHENTICATION_TOKEN']
        ),
    }
    if is_authors:
        endpoint = '/authors'
    else:
        endpoint = '/literature'
    inspirehep_url = current_app.config.get("INSPIREHEP_URL")
    if is_update:
        if not is_authors and not current_app.config.get(
            'FEATURE_FLAG_ENABLE_MERGER', False
        ):
            obj.log.info(
                'skipping update record, feature flag ``FEATURE_FLAG_ENABLE_MERGER`` is disabled.'
            )
            return
        control_number = obj.extra_data['matches']['approved']
        response = requests.put(
            "{inspirehep_url}{endpoint}/{control_number}".format(
                inspirehep_url=inspirehep_url,
                endpoint=endpoint,
                control_number=control_number
            ),
            headers=headers,
            json=obj.data
        )
        if response.status_code == 200:
            obj.data['control_number'] = response.json()['control_number']
            if response.json()['id_'] != obj.extra_data['head_uuid']:
                obj.log.warning(
                    "Record matched in workflow has different uuid than record updated in Inspirehep!"
                )
        else:
            raise WorkflowsError(
                "Response code from Inspirehep is {code}. This is wrong!"
                " Message from the server: {message}".format(
                    code=response.status_code, message=response.json()
                )
            )
    else:
        response = requests.post(
            "{inspirehep_url}{endpoint}".format(
                inspirehep_url=inspirehep_url,
                endpoint=endpoint,
            ),
            headers=headers,
            json=obj.data
        )

        if response.status_code == 201:
            obj.data['control_number'] = response.json()['control_number']
            obj.extra_data['head_uuid'] = response.json()['id_']
        else:
            raise WorkflowsError(
                "Response code from Inspirehep is {code}."
                " This is wrong! Message from the server: {message}".format(
                    code=response.status_code, message=response.json()
                )
            )
    with db.session.begin_nested():
        obj.save()


@with_debug_logging
def store_root(obj, eng):
    """Insert or update the current record head's root into the ``WorkflowsRecordSources`` table."""
    if not current_app.config.get('FEATURE_FLAG_ENABLE_MERGER', False):
        obj.log.info(
            'skipping storing source root, feature flag ``FEATURE_FLAG_ENABLE_MERGER`` is disabled.'
        )
        return

    root = obj.extra_data['merger_root']
    head_uuid = obj.extra_data['head_uuid']

    source = LiteratureReader(root).source.lower()

    if not source:
        return

    root_record = WorkflowsRecordSources(
        source=get_source_for_root(source),
        record_uuid=head_uuid,
        json=root,
    )
    db.session.merge(root_record)
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


def _is_stale_data(workflow_object):
    is_update = workflow_object.extra_data.get('is-update')
    head_version_id = workflow_object.extra_data.get('head_version_id')

    if not is_update or head_version_id is None:
        return False

    head_uuid = workflow_object.extra_data.get('head_uuid')
    record = InspireRecord.get_record(head_uuid)

    if record.model.version_id != head_version_id:
        workflow_object.log.info(
            'Working with stale data:',
            'Expecting version %d but found %d' % (
                head_version_id, record.revision_id
            )
        )
        return True
    return False


@with_debug_logging
def is_stale_data(obj, eng):
    """Check head's version_id in extra_data is the same on DB."""
    return _is_stale_data(obj)
