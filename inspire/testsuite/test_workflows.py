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

import httpretty
import os
import pkg_resources
import tempfile

from invenio.celery import celery
from invenio.testsuite import make_test_suite, run_test_suite

from .helpers import WorkflowTasksTestCase


class WorkflowTest(WorkflowTasksTestCase):

    """TODO."""

    def setUp(self):
        """Setup tests."""
        from invenio.modules.knowledge.api import add_kb

        self.create_registries()
        self.record_oai_arxiv_plots = pkg_resources.resource_string(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                'oai_arxiv_record_with_plots.xml'
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
        # Add temp KB
        add_kb('harvesting_fixture_kb')

    def tearDown(self):
        """Clean up created objects."""
        from invenio.modules.workflows.models import Workflow
        from invenio.modules.knowledge.api import delete_kb

        self.delete_objects(
            Workflow.get(Workflow.module_name == 'unit_tests').all())
        self.cleanup_registries()
        delete_kb('harvesting_fixture_kb')

    def test_payload_creation(self):
        """TODO."""
        from invenio.modules.workflows.api import start
        from invenio.modules.workflows.engine import WorkflowStatus

        workflow = start('payload_fixture',
                         data=[self.some_record],
                         module_name="unit_tests")

        self.assertEqual(WorkflowStatus.COMPLETED, workflow.status)
        self.assertTrue(len(workflow.completed_objects) == 1)
        modified_object = workflow.completed_objects[0]

        for l in ['files', 'sips', 'type', 'drafts', 'title']:
            self.assertIn(l, modified_object.data)

    def test_payload_sip_creation(self):
        """TODO."""
        from invenio.modules.workflows.api import start
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
        """TODO."""
        from invenio.modules.workflows.api import start

        workflow = start('payload_model_fixture',
                         data=[self.some_record],
                         module_name="unit_tests")
        modified_object = workflow.completed_objects[0]

        p = workflow.workflow_definition.model(modified_object)
        sip = p.get_latest_sip()
        self.assertTrue(sip.metadata)
        # self.assertTrue(sip.package)

    def test_payload_file_creation(self):
        """TODO."""
        from invenio.modules.workflows.models import BibWorkflowObject
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
    def test_harvesting_workflow(self):
        """Test a full harvesting workflow."""
        from invenio.base.globals import cfg
        from invenio.modules.workflows.api import start
        from inspire.utils.helpers import (
            get_record_from_obj,
        )

        # XXX(jacquerie): apparently we never perform_request.
        # httpretty.register_uri(
        #     httpretty.GET,
        #     cfg['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
        #     body='',
        #     status=200
        # )

        httpretty.register_uri(
            httpretty.GET,
            'http://arxiv.org/e-print/1407.7587',
            content_type="application/x-eprint-tar",
            body=self.arxiv_tarball.read(),
            status=200,
            adding_headers={
                "Content-Encoding": 'x-gzip',
            }
        )

        httpretty.register_uri(
            httpretty.GET,
            'http://arxiv.org/pdf/1407.7587.pdf',
            content_type="application/pdf",
            body=self.arxiv_pdf.read(),
            status=200,
        )

        httpretty.register_uri(
            httpretty.POST,
            cfg.get("CFG_ROBOTUPLOAD_SUBMISSION_BASEURL"),
            body="[INFO] bibupload batchupload --insert /dummy/file/path\n",
            status=200,
        )
        workflow = start('harvesting_fixture',
                         data=[self.record_oai_arxiv_plots],
                         module_name='unit_tests')

        # Let's get the record metadata and check contents
        obj = workflow.halted_objects[0]
        record = get_record_from_obj(obj, workflow)

        # Files should have been attached (tarball + pdf)
        self.assertTrue(len(obj.data["files"]) == 2)

        # Some plots/files should have been added to FFTs
        self.assertTrue(record.get('fft'))

        # A publication note should have been extracted
        self.assertTrue(record.get('publication_info'))

        # A prediction should have been made
        self.assertTrue(obj.get_tasks_results().get("arxiv_guessing"))

        # Now let's resolve it as accepted and continue
        obj.remove_action()
        obj.extra_data["approved"] = True
        obj.extra_data["core"] = True
        obj.set_extra_data(obj.extra_data)
        obj.save()
        workflow = obj.continue_workflow()

        record = get_record_from_obj(obj, workflow)
        self.assertTrue("CORE" in record.get("collections.primary"))

    @httpretty.activate
    def test_sss_harvesting_workflow_sad(self):
        """TODO."""
        from invenio.modules.workflows.api import start

        httpretty.HTTPretty.allow_net_connect = False

        # XXX(jacquerie): apparently we never perform_request.
        # httpretty.register_uri(
        #     httpretty.GET,
        #     cfg['WORKFLOWS_MATCH_REMOTE_SERVER_URL'],
        #     body='[1212]',
        #     status=200
        # )

        workflow = start('harvesting_fixture',
                         data=[self.record_oai_arxiv_plots],
                         module_name='unit_tests')
        # XXX(jacquerie): find a better check
        self.assertEqual(workflow.objects, [])


class AgnosticTest(WorkflowTasksTestCase):

    """TODO."""

    def setUp(self):
        """Setup tests."""
        from invenio.modules.deposit.models import Deposition, DepositionType
        from invenio.modules.deposit.registry import deposit_types, \
            deposit_default_type
        from invenio.modules.deposit.form import WebDepositForm
        from invenio.modules.deposit.tasks import prefill_draft, \
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
        from invenio.modules.workflows.models import Workflow
        from invenio.modules.knowledge.api import delete_kb

        self.cleanup_registries()

    def test_agnostic_deposit(self):
        """TODO."""
        from invenio.modules.workflows.api import start
        from invenio.modules.deposit.models import Deposition
        from invenio.ext.login.legacy_user import UserInfo

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
