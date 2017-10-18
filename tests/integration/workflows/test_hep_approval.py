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

"""Tests for hep_approval action."""

from __future__ import absolute_import, division, print_function

import StringIO
import pytest

from invenio_db import db
from invenio_workflows import workflow_object_class
from invenio_workflows.models import WorkflowObjectModel

from inspirehep.modules.workflows.actions.hep_approval import HEPApproval


@pytest.fixture(scope='function')
def workflow():
    workflow_object = workflow_object_class.create(
        data={},
        id_user=1,
        data_type="hep"
    )
    workflow_object.save()
    db.session.commit()
    workflow_object.continue_workflow = lambda **args: True

    yield workflow_object

    WorkflowObjectModel.query.filter_by(id=workflow_object.id).delete()
    db.session.commit()


def test_resolve_accept(small_app, workflow):
    args = {
        'request_data': {
            'value': 'accept',
        }
    }
    HEPApproval.resolve(workflow, **args)
    expected = {
        'core': False,
        'user_action': 'accept',
        'upload_pdf': False,
        '_action': None,
        '_message': '',
        'reason': '',
        'approved': True
    }
    assert workflow.extra_data == expected


def test_resolve_accept_core(small_app, workflow):
    args = {
        'request_data': {
            'value': 'accept_core'
        }
    }
    HEPApproval.resolve(workflow, **args)
    expected = {
        'core': True,
        'user_action': 'accept_core',
        'upload_pdf': False,
        '_action': None,
        '_message': '',
        'reason': '',
        'approved': True
    }
    assert workflow.extra_data == expected


def test_resolve_rejected(small_app, workflow):
    args = {
        'request_data': {
            'value': 'rejected',
            'reason': 'Duplicated article'
        }
    }
    HEPApproval.resolve(workflow, **args)
    expected = {
        'core': False,
        'user_action': 'rejected',
        'upload_pdf': False,
        '_action': None,
        '_message': '',
        'reason': 'Duplicated article',
        'approved': False
    }
    assert workflow.extra_data == expected


def test_resolve_attach_pdf(small_app, workflow):
    args = {
        'request_data': {
            'value': 'accept',
            'pdf_upload': True
        }
    }
    workflow.data = {
        'documents': [{
            'key': 'fulltext.pdf'
        }]
    }
    workflow.files['fulltext.pdf'] = StringIO.StringIO()
    HEPApproval.resolve(workflow, **args)
    expected = {
        'core': False,
        'user_action': 'accept',
        'upload_pdf': True,
        '_action': None,
        '_message': '',
        'reason': '',
        'approved': True
    }

    assert workflow.extra_data == expected
    assert 'fulltext.pdf' in workflow.files
    assert 'fulltext.pdf' in [doc['key'] for doc in workflow.data['documents']]


def test_resolve_remove_pdf(small_app, workflow):
    args = {
        'request_data': {
            'value': 'accept',
            'pdf_upload': False
        }
    }
    workflow.data = {
        'documents': [{
            'key': 'fulltext.pdf'
        }]
    }
    workflow.files['fulltext.pdf'] = StringIO.StringIO()
    HEPApproval.resolve(workflow, **args)
    expected = {
        'core': False,
        'user_action': 'accept',
        'upload_pdf': False,
        '_action': None,
        '_message': '',
        'reason': '',
        'approved': True
    }

    assert workflow.extra_data == expected
    assert 'fulltext.pdf' not in workflow.files
    assert 'fulltext.pdf' not in [doc['key'] for doc in workflow.data['documents']]
