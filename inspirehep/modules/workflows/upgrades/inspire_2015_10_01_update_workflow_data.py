# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Migrate bibfield data model to new doJSON data model in workflows."""

from __future__ import absolute_import, print_function, unicode_literals

from invenio_workflows.models import (
    BibWorkflowObject,
    Workflow
)
from inspirehep.modules.migrator.tasks import migrate_workflow_object

depends_on = []


def info():
    """Info about this upgrade."""
    return __doc__


def do_upgrade():
    """Implement your upgrades here."""
    workflows_to_fix = [
        "process_record_arxiv", "literature",
        "authornew", "authorupdate"
    ]
    workflow_objects = []
    for workflow_name in workflows_to_fix:
        workflow_objects += BibWorkflowObject.query.with_entities(
            BibWorkflowObject.id
        ).join(
            BibWorkflowObject.workflow
        ).filter(Workflow.name == workflow_name).all()

    for obj in workflow_objects:
        migrate_workflow_object.delay(obj)


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return BibWorkflowObject.query.count()


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    pass


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    pass
