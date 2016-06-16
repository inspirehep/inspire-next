# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Unified data model in workflow, based on Deposition model."""

import os
import six

from flask import render_template

from invenio_base.globals import cfg

from invenio_deposit.models import (
    Agent,
    Deposition,
    DepositionDraft,
    DepositionFile,
    DepositionStorage,
    SubmissionInformationPackage,
    InvalidDepositionType,
)
from invenio_deposit.storage import Storage

from invenio_formatter import format_record

from inspirehep.utils.helpers import get_record_from_model


def create_payload(obj, eng):
    """Create a proper data model inside obj.data."""
    p = Payload.create(workflow_object=obj, type=eng.name)
    p.update()


class PayloadStorage(Storage):

    """Payload storage backend.

    Saves files to a folder (<WORKFLOWS_STORAGEDIR>/<payload_id>/).
    """

    def __init__(self, payload_id):
        """Initialize storage."""
        payload_hash = str(payload_id)
        self.fs_path = os.path.join(
            cfg['WORKFLOWS_STORAGEDIR'],
            payload_hash[:2],
            payload_hash[2:4],
            payload_hash[4:6],
            payload_hash
        )


class Payload(Deposition):

    """Wrap a BibWorkflowObject."""

    def __init__(self, workflow_object, type=None, user_id=None):
        """Create a new Payload object."""
        self.files = []
        self.drafts = {}
        self.type = self.get_type(type)
        self.title = ''
        self.sips = []
        super(Payload, self).__init__(workflow_object, self.type, user_id)

    @classmethod
    def get_type(self, type_or_id):
        """Get type."""
        from invenio_workflows.registry import workflows
        return workflows.get(type_or_id)

    @classmethod
    def create(cls, user=None, type=None, workflow_object=None):
        """Create a new payload object."""
        if user is not None:
            user = user.get_id()

        if workflow_object:
            sip = SubmissionInformationPackage(metadata=workflow_object.data)
            workflow_object.data = {
                "sips": [sip.__getstate__()],
                "files": [],
                "title": "",
                "drafts": {},
                "type": type,
            }
            workflow_object.set_data(workflow_object.data)
            if workflow_object.id is None:
                workflow_object.save()

        # Note: it is correct to pass 'type' and not 't' below to constructor.
        obj = cls(workflow_object=workflow_object, type=type, user_id=user)
        return obj

    def __setstate__(self, state):
        """Deserialize deposition from state stored in BibWorkflowObject."""
        self.type = self.get_type(state['type'])  # FIXME only difference
        self.title = state['title']
        self.files = [
            DepositionFile.factory(
                f_state,
                uuid=f_state['id'],
                backend=DepositionStorage(self.id),
            )
            for f_state in state['files']
        ]
        self.drafts = dict(
            [(d_id, DepositionDraft.factory(d_state, d_id,
                                            deposition_ref=self))
             for d_id, d_state in state['drafts'].items()]
        )
        self.sips = [
            SubmissionInformationPackage.factory(s_state, uuid=s_state['id'])
            for s_state in state.get('sips', [])
        ]

    def prepare_sip(self, from_request_context=False):
        """Prepare Payload Submission Information Package."""
        sip = self.get_latest_sip()
        if sip is None:
            sip = self.create_sip()

        if 'files' in sip.metadata:
            sip.metadata['fft'] = sip.metadata['files']
            del sip.metadata['files']

        sip.agents = [Agent(role='creator',
                            from_request_context=from_request_context)]
        self.update()


class SIPWorkflowMixin(object):

    """Base mixin for workflow definitions using SIP as their data models."""

    @classmethod
    def get_title(cls, obj, **kwargs):
        """Return the value to put in the title column of Holding Pen."""
        if not hasattr(obj, "data"):
            obj.data = obj.get_data()
        if isinstance(obj.data, dict):
            try:
                model = cls.model(obj)
            except InvalidDepositionType:
                return "This submission is disabled: {0}.".format(obj.workflow.name)
            record = get_record_from_model(model)
            if record:
                titles = filter(None, record.get("titles.title", []))
                if titles:
                    # Show first title that evaluates to True
                    return titles[0]
        return "No title available"

    @classmethod
    def get_description(cls, obj, **kwargs):
        """Return the value to put in the description column of HoldingPen."""
        return "No description"

    @classmethod
    def get_additional(cls, obj, **kwargs):
        """Return the value to put in the additional column of HoldingPen."""
        from inspirehep.modules.predicter.utils import get_classification_from_task_results
        keywords = get_classification_from_task_results(obj)
        results = obj.get_tasks_results()
        prediction_results = results.get("arxiv_guessing", {})
        if prediction_results:
            prediction_results = prediction_results[0].get("result")
        return render_template(
            'workflows/styles/harvesting_record_additional.html',
            object=obj,
            keywords=keywords,
            score=prediction_results.get("max_score"),
            decision=prediction_results.get("decision")
        )

    @classmethod
    def formatter(cls, obj, **kwargs):
        """Nicely format the record."""
        try:
            model = cls.model(obj)
            record = get_record_from_model(model)
        except TypeError as err:
            return "Error: {0}".format(err)
        if not record:
            return ""
        if kwargs.get('of'):
            if "recid" not in record:
                record['recid'] = None
            return format_record(record=record, of=kwargs.get('of'))
        return render_template(
            'format/record/Holding_Pen_HTML_detailed.tpl',
            record=record
        )

    @classmethod
    def get_sort_data(cls, obj, **kwargs):
        """Return a dictionary useful for sorting in Holding Pen."""
        results = obj.get_tasks_results()
        prediction_results = results.get("arxiv_guessing", {})
        if prediction_results:
            prediction_results = prediction_results[0].get("result")
            max_score = prediction_results.get("max_score")
            decision = prediction_results.get("decision")
            relevance_score = max_score
            if decision == "CORE":
                relevance_score += 10
            elif decision == "Rejected":
                relevance_score = (max_score * -1) - 10
            return {
                "max_score": prediction_results.get("max_score"),
                "decision": prediction_results.get("decision"),
                "relevance_score": relevance_score
            }
        else:
            return {}

    @classmethod
    def get_record(cls, obj, **kwargs):
        """Return a dictionary-like object representing the current object.

        This object will be used for indexing and be the basis for display
        in Holding Pen.
        """
        if not hasattr(obj, "data"):
            obj.data = obj.get_data()
        if isinstance(obj.data, six.text_type):
            return {}
        model = cls.model(obj)
        record = get_record_from_model(model)
        if record:
            return record.dumps()
        else:
            return {}
