# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage harvester module."""

from __future__ import print_function

import sys

from invenio.base.globals import cfg

from invenio.modules.workflows.registry import workflows
from invenio.ext.script import Manager

from .utils import validate_date
from .tasks import run_harvest


manager = Manager(usage=__doc__)


def get_harvesting_workflows():
    """Return the workflows enabled in the harvester module."""
    enabled_workflows = []
    for name in cfg.get("HARVESTER_WORKFLOWS", list()):
        if workflows.get(name):
            enabled_workflows.append(name)
    return enabled_workflows


@manager.option('--workflow', '-w', dest='workflow')
@manager.option('--from', '-f', dest='from_date',
                help='Get records from this date and on.')
@manager.option('--to', '-t', dest='to_date',
                help='Get records until this date.')
def run(workflow, from_date, to_date):
    """Run a harvesting workflow from the command line.

    Usage: inveniomanage harvester run -w workflow_name -f 2014-01-01 -t 2014-12-31
    """
    if not workflow:
        print("Missing workflow!", file=sys.stderr)
        print("Usage: inveniomanage harvester run -w workflow_name -f 2014-01-01 -t 2014-12-31")
        list_workflows()
        return
    if workflow not in get_harvesting_workflows():
        print("* Invalid workflow name",
              file=sys.stderr)
        list_workflows()
        return

    if from_date:
        validate_date(from_date)
    if to_date:
        validate_date(to_date)

    args = {
        "workflow": workflow,
        "from_date": from_date,
        "to_date": to_date
    }

    job = run_harvest.delay(**args)
    print("Scheduled job {0} with args: {1}".format(job.id, args))


@manager.command
def list_workflows():
    """List available workflows."""
    print("Available workflows:")
    for name in get_harvesting_workflows():
        print(name)
