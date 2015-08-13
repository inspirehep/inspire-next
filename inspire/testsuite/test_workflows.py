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

import os
import pkg_resources

from flask_registry import ImportPathRegistry

from invenio.celery import celery
from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

from invenio.modules.workflows.registry import WorkflowsRegistry

TEST_PACKAGES = [
    'inspire.modules.*',
    'inspire.testsuite',
]


class WorkflowTasksTestCase(InvenioTestCase):

    """ Workflow class for testing."""

    def create_registries(self):
        """Create registries for testing."""
        self.app.extensions['registry']['workflows.tests'] = \
            ImportPathRegistry(initial=TEST_PACKAGES)
        self.app.extensions['registry']['workflows'] = \
            WorkflowsRegistry(
                'workflows', app=self.app, registry_namespace='workflows.tests'
            )
        self.app.extensions['registry']['workflows.actions'] = \
            WorkflowsRegistry(
                'actions', app=self.app, registry_namespace='workflows.tests'
            )

    def cleanup_registries(self):
        """Clean registries for testing."""
        del self.app.extensions['registry']['workflows.tests']
        del self.app.extensions['registry']['workflows']
        del self.app.extensions['registry']['workflows.actions']


class WorkflowTest(WorkflowTasksTestCase):

    """Class to test the delayed workflows."""

    def setUp(self):
        """ Setup tests."""
        self.create_registries()
        self.some_record = pkg_resources.resource_string(
            'inspire.testsuite',
            os.path.join(
                'workflows',
                'fixtures',
                'some_record.xml'
            )
        )
        celery.conf['CELERY_ALWAYS_EAGER'] = True

    def tearDown(self):
        """ Clean up created objects."""
        from invenio.modules.workflows.models import Workflow
        self.delete_objects(
            Workflow.get(Workflow.module_name == "unit_tests").all())
        self.cleanup_registries()

    def test_payload_creation(self):
        from invenio.modules.workflows.api import start
        from invenio.modules.workflows.engine import WorkflowStatus

        workflow = start('payload_fixture', data=[self.some_record])

        self.assertEqual(WorkflowStatus.COMPLETED, workflow.status)


TEST_SUITE = make_test_suite(WorkflowTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
