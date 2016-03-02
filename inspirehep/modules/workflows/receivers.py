# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014. 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Signal receivers for workflows."""


from flask import current_app

from sqlalchemy.event import listen

from invenio_workflows.models import BibWorkflowObject, ObjectVersion
from invenio_workflows.signals import (
    workflow_object_saved,
    workflow_halted
)


def continue_workflow(sender, **kwargs):
    """Continue a workflow object if halted at a specific task."""
    if hasattr(sender, "last_task"):
        task = sender.last_task
        if task == 'halt_to_render':
            sender.continue_workflow(delayed=True)


def precache_holdingpen_row(sender, **kwargs):
    """Precache a Holding Pen row."""
    from invenio_workflows.utils import get_formatted_holdingpen_object
    # Call it to cache it
    get_formatted_holdingpen_object(sender)


def delete_from_index(mapper, connection, target):
    """Delete record from index."""
    from invenio_ext.es import es

    indices = set(current_app.config['SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING'].values())
    indices.add(current_app.config['SEARCH_ELASTIC_DEFAULT_INDEX'])

    doc_type = current_app.config.get(
        "WORKFLOWS_HOLDING_PEN_DOC_TYPE"
    )
    for index in indices:
        index = current_app.config['WORKFLOWS_HOLDING_PEN_ES_PREFIX'] + index
        es.delete(
            index=index,
            doc_type=doc_type,
            id=target.id,
            ignore=404
        )


@workflow_object_saved.connect
def index_holdingpen_record(sender, **kwargs):
    """Index a Holding Pen record."""
    from invenio_ext.es import es
    from invenio_records.api import Record
    from invenio_records.signals import before_record_index
    from invenio_records.recordext.functions.get_record_collections import (
        get_record_collections,
    )
    from invenio_records.tasks.index import get_record_index

    from invenio_workflows.registry import workflows

    if not sender.workflow:
        # No workflow registered to object yet. Skip indexing
        return

    if sender.version == ObjectVersion.INITIAL:
        # Ignore initial versions
        return

    workflow = workflows.get(sender.workflow.name)
    if not workflow:
        current_app.logger.info(
            "Workflow {0} not found for sender: {1}".format(
                sender.workflow.name, sender.id
            )
        )
        return

    if not hasattr(sender, 'data'):
        sender.data = sender.get_data()
    if not hasattr(sender, 'extra_data'):
        sender.extra_data = sender.get_extra_data()

    record = Record({})
    record["version"] = ObjectVersion.name_from_version(sender.version)
    record["type"] = sender.data_type
    record["status"] = sender.status
    record["created"] = sender.created.isoformat()
    record["modified"] = sender.modified.isoformat()
    record["uri"] = sender.uri
    record["id_workflow"] = sender.id_workflow
    record["id_user"] = sender.id_user
    record["id_parent"] = sender.id_parent
    record["workflow"] = sender.workflow.name
    try:
        record.update(workflow.get_record(sender))
    except Exception as err:
        current_app.logger.exception(err)

    try:
        record.update(workflow.get_sort_data(sender))
    except Exception as err:
        current_app.logger.exception(err)

    # Add collection to get correct mapping
    record["_collections"] = get_record_collections(record)

    if hasattr(workflow, "search_index"):
        record_index = workflow.search_index
    else:
        # Depends on "_collections" being filled correctly for record
        record_index = get_record_index(record)

    # Trigger any before_record_index receivers
    before_record_index.send(sender.id, json=record, index=record_index)

    if record_index:
        # Delete from other indexes in case index changed.
        delete_from_index(None, None, sender)
        index = current_app.config['WORKFLOWS_HOLDING_PEN_ES_PREFIX'] + record_index
        es.index(
            index=index,
            doc_type=current_app.config["WORKFLOWS_HOLDING_PEN_DOC_TYPE"],
            body=dict(record),
            id=sender.id
        )

workflow_halted.connect(precache_holdingpen_row)
workflow_halted.connect(continue_workflow)
listen(BibWorkflowObject, "after_delete", delete_from_index)
