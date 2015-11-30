# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Test helpers."""

import sys

from importlib import import_module

from flask_registry import ImportPathRegistry

from invenio.testsuite import InvenioTestCase


TEST_PACKAGES = [
    'tests',
]


def reimport_module(module_name):
    """Import a module to use as a mock without `sys.modules` cache."""
    try:
        del sys.modules[module_name]
    except KeyError:
        pass
    return import_module(module_name)


class WorkflowTasksTestCase(InvenioTestCase):

    """ Workflow class for testing."""

    def create_registries(self):
        """Create registries for testing."""
        from invenio_workflows.registry import WorkflowsRegistry
        self.app.extensions['registry']['workflows.tests'] = ImportPathRegistry(
            initial=TEST_PACKAGES
        )
        self.app.extensions['registry']['workflows'] = WorkflowsRegistry(
            'workflows', app=self.app, registry_namespace='workflows.tests'
        )
        self.app.extensions['registry']['workflows.actions'] = WorkflowsRegistry(
            'actions', app=self.app, registry_namespace='workflows.tests'
        )

    def cleanup_registries(self):
        """Clean registries for testing."""
        del self.app.extensions['registry']['workflows.tests']
        del self.app.extensions['registry']['workflows']
        del self.app.extensions['registry']['workflows.actions']
