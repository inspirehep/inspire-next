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

"""Tests for WorkflowsAudit model."""

from __future__ import absolute_import, division, print_function

from invenio_db import db

from invenio_accounts.models import User
from invenio_workflows import workflow_object_class

from inspirehep.modules.workflows.models import WorkflowsAudit
from inspirehep.modules.workflows.utils import log_workflows_action


def test_audit(small_app):
    user_id = None
    workflow_id = None
    with small_app.app_context():
        user = User(email="test@example.com", active=True)
        user.password = "test"
        db.session.add(user)

        workflows_object = workflow_object_class.create({}, data_type="hep")
        db.session.commit()

        user_id = user.id
        workflow_id = workflows_object.id

    with small_app.app_context():
        logging_info = {
            'object_id': workflow_id,
            'user_id': user_id,
            'score': 0.222113,
            'user_action': "Non-CORE",
            'decision': "Rejected",
            'source': "test",
            'action': "accept"
        }
        audit = WorkflowsAudit(**logging_info)
        audit.save()
        db.session.commit()

        assert WorkflowsAudit.query.count() == 1

        audit_entry = WorkflowsAudit.query.filter(
            WorkflowsAudit.object_id == workflow_id
        ).one()
        assert audit_entry
        assert audit_entry.action == "accept"
        assert audit_entry.score == 0.222113

    relevance_prediction = dict(
        max_score=0.222113, decision="Rejected"
    )
    with small_app.app_context():
        log_workflows_action(
            action="accept_core",
            relevance_prediction=relevance_prediction,
            object_id=workflow_id,
            user_id=None,
            source="test",
            user_action="accept"
        )
        db.session.commit()

        assert WorkflowsAudit.query.count() == 2

        audit_entry = WorkflowsAudit.query.filter(
            WorkflowsAudit.action == "accept_core"
        ).one()
        assert audit_entry
        assert audit_entry.action == "accept_core"
        assert audit_entry.score == 0.222113
