# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2022 CERN.
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

"""Tests for hep_approval action."""

from __future__ import absolute_import, division, print_function

import pytest
from invenio_db import db
from invenio_workflows import workflow_object_class
from invenio_workflows.models import WorkflowObjectModel

from inspirehep.modules.workflows.actions.core_selection_approval import \
    CoreSelectionApproval


@pytest.fixture(scope="function")
def workflow():
    workflow_object = workflow_object_class.create(data={}, id_user=1, data_type="hep")
    workflow_object.save()
    db.session.commit()
    workflow_object.continue_workflow = lambda **args: True

    yield workflow_object

    WorkflowObjectModel.query.filter_by(id=workflow_object.id).delete()
    db.session.commit()


def test_resolve_accept_core(workflow_app, workflow):
    args = {
        "request_data": {
            "value": "accept_core",
        }
    }
    CoreSelectionApproval.resolve(workflow, **args)
    expected = {
        "core": True,
        "_action": None,
        "_message": "",
        "reason": "",
        "user_action": "accept_core",
    }
    assert workflow.extra_data == expected


def test_resolve_accept(workflow_app, workflow):
    args = {
        "request_data": {
            "value": "accept",
        }
    }
    CoreSelectionApproval.resolve(workflow, **args)
    expected = {
        "core": False,
        "_action": None,
        "_message": "",
        "reason": "",
        "user_action": "accept",
    }
    assert workflow.extra_data == expected
