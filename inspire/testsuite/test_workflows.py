# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

"""Tests for workflows."""

from __future__ import print_function, absolute_import

import re
import os
import pkg_resources
import tempfile

import httpretty
import responses

from invenio_celery import celery
from invenio.testsuite import make_test_suite, run_test_suite

from mock import patch

from .helpers import WorkflowTasksTestCase


class WorkflowTest(WorkflowTasksTestCase):

    """Test the Payload class.

    The Payload class, derived from the Deposition class representing a user
    submission, can be used to represent the result of harvesting a record in
    a workflow.

    These two classes share their data model and have similar APIs.
    """

    def setUp(self):
        """Setup tests."""
        from inspire.modules.workflows.receivers import precache_holdingpen_row
        from invenio_workflows.receivers import index_holdingpen_record
        from invenio_workflows.signals import (
            workflow_halted,
            workflow_object_saved
        )

        # Disable the holdingpen caching receiver.
        workflow_halted.disconnect(precache_holdingpen_row)
        workflow_object_saved.disconnect(index_holdingpen_record)

        self.create_registries()
        self.record_oai_arxiv_plots = pkg_resources.resource_string(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                'oai_arxiv_record_with_plots.xml'
            )
        )
        self.record_oai_arxiv_accept = pkg_resources.resource_string(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                'oai_arxiv_record_to_accept.xml'
            )
        )
        self.some_record = pkg_resources.resource_string(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                'some_record.xml'
            )
        )
        self.arxiv_tarball = pkg_resources.resource_stream(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                '1407.7587v1'
            )
        )
        self.arxiv_pdf = pkg_resources.resource_stream(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                '1407.7587v1.pdf'
            )
        )
        self.arxiv_tarball_accept = pkg_resources.resource_stream(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                '1511.01097'
            )
        )
        self.arxiv_pdf_accept = pkg_resources.resource_stream(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                '1511.01097v1.pdf'
            )
        )

    def tearDown(self):
        """Clean up created objects."""
        from invenio_workflows.models import Workflow
        from inspire.modules.workflows.receivers import precache_holdingpen_row
        from invenio_workflows.receivers import index_holdingpen_record
        from invenio_workflows.signals import (
            workflow_halted,
            workflow_object_saved
        )

        workflow_halted.connect(precache_holdingpen_row)
        workflow_object_saved.connect(index_holdingpen_record)

        self.delete_objects(
            Workflow.get(Workflow.module_name == 'unit_tests').all())
        self.cleanup_registries()

    def test_payload_creation(self):
        """A Payload can be created."""
        from invenio_workflows.api import start
        from invenio_workflows.engine import WorkflowStatus

        workflow = start('payload_fixture',
                         data=[self.some_record],
                         module_name="unit_tests")

        self.assertEqual(WorkflowStatus.COMPLETED, workflow.status)
        self.assertTrue(len(workflow.completed_objects) == 1)
        modified_object = workflow.completed_objects[0]

        for l in ['files', 'sips', 'type', 'drafts', 'title']:
            self.assertIn(l, modified_object.data)

    def test_payload_sip_creation(self):
        """A Payload has a sip."""
        from invenio_workflows.api import start
        from inspire.modules.workflows.models import Payload

        workflow = start('payload_fixture',
                         data=[self.some_record],
                         module_name="unit_tests")
        modified_object = workflow.completed_objects[0]

        p = Payload(modified_object)
        sip = p.get_latest_sip()
        self.assertTrue(sip.metadata)
        # self.assertTrue(sip.package)

    def test_payload_model_creation(self):
        """A workflow can specify a model to encapsulate behaviour."""
        from invenio_workflows.api import start

        workflow = start('payload_model_fixture',
                         data=[self.some_record],
                         module_name="unit_tests")
        modified_object = workflow.completed_objects[0]

        p = workflow.workflow_definition.model(modified_object)
        sip = p.get_latest_sip()
        self.assertTrue(sip.metadata)
        # self.assertTrue(sip.package)

    def test_payload_file_creation(self):
        """Can add a file to a Payload."""
        from invenio_workflows.models import BibWorkflowObject
        from inspire.modules.workflows.models import Payload
        from inspire.utils.helpers import (
            get_file_by_name,
            add_file_by_name,
        )

        obj = BibWorkflowObject.create_object()
        obj.save()
        obj.data = obj.get_data()  # FIXME hack until workflow 2.0

        payload = Payload.create(workflow_object=obj, type="payload_fixture")
        payload.save()

        fd, filename = tempfile.mkstemp()
        os.close(fd)

        newpath = add_file_by_name(payload, filename)
        self.assertTrue(newpath)

        self.assertTrue(get_file_by_name(payload,
                                         os.path.basename(filename)))
        BibWorkflowObject.delete(obj)

    @httpretty.activate
    def test_harvesting_workflow_with_match(self):
        """Test an harvesting workflow when the record already exists."""
        from invenio_base.globals import cfg
        from invenio_workflows.api import start

        # Mock Elasticsearch DELETE hook
        httpretty.register_uri(
            httpretty.DELETE,
            re.compile(".*holdingpen/record/(\d+)"),
            status=404
        )

        httpretty.register_uri(
            httpretty.GET,
            cfg['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
            body='[1212]',
            status=200
        )

        workflow = start('harvesting_fixture',
                         data=[self.record_oai_arxiv_plots],
                         module_name='unit_tests')
        # XXX(jacquerie): find a better check
        self.assertEqual(workflow.objects, [])

    @responses.activate
    @patch('invenio_workflows.search.search')
    def test_harvesting_workflow_rejected(self, search):
        """Test a full harvesting workflow."""
        from invenio_base.globals import cfg
        from invenio_workflows.api import start
        from inspire.utils.helpers import (
            get_record_from_obj,
        )

        # Mock Elasticsearch search for Holding Pen check
        search.return_value = []

        responses.add(
            responses.GET,
            cfg['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
            body='[]',
            status=200
        )

        responses.add(
            responses.GET,
            'http://arxiv.org/e-print/1407.7587',
            content_type="application/x-eprint-tar",
            body=self.arxiv_tarball.read(),
            status=200,
            adding_headers={
                "Content-Encoding": 'x-gzip',
            },
        )

        responses.add(
            responses.GET,
            'http://arxiv.org/pdf/1407.7587',
            content_type="application/pdf",
            body=self.arxiv_pdf.read(),
            status=200,
            stream=True,
        )

        workflow = start('harvesting_fixture',
                         data=[self.record_oai_arxiv_plots],
                         module_name='unit_tests')

        # Let's get the record metadata and check contents
        obj = workflow.completed_objects[0]
        record = get_record_from_obj(obj, workflow)

        # This record should be rejected
        self.assertFalse(obj.extra_data["approved"])

        # Files should have been attached (tarball + pdf)
        self.assertTrue(len(obj.data["files"]) == 2)

        # Some plots/files should have been added to FFTs
        self.assertTrue(record.get('fft'))

        # A publication note should have been extracted
        self.assertTrue(record.get('publication_info'))

        # A prediction should have been made
        self.assertTrue(obj.get_tasks_results().get("arxiv_guessing"))

        # It is not CORE
        self.assertFalse("CORE" in record.get("collections.primary"))

    @responses.activate
    @patch('invenio_workflows.search.search')
    def test_harvesting_workflow_accepted(self, search):
        """Test a full harvesting workflow."""
        from invenio_base.globals import cfg
        from invenio_workflows.api import start
        from inspire.utils.helpers import (
            get_record_from_obj,
        )

        # Mock Elasticsearch search for Holding Pen check
        search.return_value = []

        responses.add(
            responses.GET,
            cfg['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
            body='[]',
            status=200
        )

        responses.add(
            responses.GET,
            'http://arxiv.org/e-print/1511.01097',
            content_type="application/x-eprint-tar",
            body=self.arxiv_tarball_accept.read(),
            status=200,
            adding_headers={
                "Content-Encoding": 'x-gzip',
            },
        )

        responses.add(
            responses.GET,
            'http://arxiv.org/pdf/1511.01097',
            content_type="application/pdf",
            body=self.arxiv_pdf_accept.read(),
            status=200,
            stream=True,
        )

        robotupload_url = os.path.join(
            cfg.get("CFG_ROBOTUPLOAD_SUBMISSION_BASEURL"),
            "batchuploader/robotupload/insert"
        )

        responses.add(
            responses.POST,
            robotupload_url,
            body="[INFO] bibupload batchupload --insert /dummy/file/path\n",
            status=200,
        )
        workflow = start('harvesting_fixture',
                         data=[self.record_oai_arxiv_accept],
                         module_name='unit_tests')

        # Let's get the halted record
        obj = workflow.halted_objects[0]

        # Now let's resolve it as accepted and continue
        obj.remove_action()
        obj.extra_data["approved"] = True
        obj.extra_data["core"] = True
        obj.set_extra_data(obj.extra_data)
        obj.save()
        workflow = obj.continue_workflow()

        record = get_record_from_obj(obj, workflow)
        # Now it is CORE
        self.assertTrue("CORE" in record.get("collections.primary"))


class AgnosticTest(WorkflowTasksTestCase):

    """Test that the data model can still accept a deposition."""

    def setUp(self):
        """Setup tests."""
        from invenio_deposit.models import Deposition, DepositionType
        from invenio_deposit.registry import deposit_types, \
            deposit_default_type
        from invenio_deposit.form import WebDepositForm
        from invenio_deposit.tasks import prefill_draft, \
            prepare_sip

        celery.conf['CELERY_ALWAYS_EAGER'] = True

        def agnostic_task(obj, eng):
            data_model = eng.workflow_definition.model(obj)
            sip = data_model.get_latest_sip()
            print(sip.metadata)

        class DefaultType(DepositionType):
            pass

        class SimpleRecordTestForm(WebDepositForm):
            pass

        class DepositModelTest(DepositionType):

            """A test workflow for the model."""

            model = Deposition

            draft_definitions = {
                'default': SimpleRecordTestForm,
            }

            workflow = [
                prefill_draft(draft_id='default'),
                prepare_sip(),
                agnostic_task,
            ]

        deposit_types.register(DefaultType)
        deposit_types.register(DepositModelTest)
        deposit_default_type.register(DefaultType)

    def teardown(self):
        """Clean up created objects."""
        self.cleanup_registries()

    def test_agnostic_deposit(self):
        """A deposition still has the same data model."""
        from invenio_deposit.models import Deposition
        from invenio_ext.login.legacy_user import UserInfo

        u = UserInfo(uid=1)
        d = Deposition.create(u, type='DepositModelTest')
        d.save()
        d.run_workflow()

        completed_object = d.engine.completed_objects[0]
        for l in ['files', 'sips', 'type', 'drafts', 'title']:
            self.assertIn(l, completed_object.data)


TEST_SUITE = make_test_suite(AgnosticTest, WorkflowTest)


if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
