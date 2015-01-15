# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""Manage harvester module."""


from invenio.modules.workflows.registry import workflows
from invenio.ext.script import Manager
from invenio.modules.workflows.api import start_delayed
from invenio.modules.workflows.models import BibWorkflowObject

manager = Manager(usage=__doc__)


def get_harvesting_workflows():
    """Return the workflows defined in the harvester module."""
    result = workflows.items()
    #filter out the workflows defined as dictionaries
    #only workflows defined as classes should remain
    result = filter(lambda a: not isinstance(a[1], dict), result)
    #get from each class the module it belongs
    result = map(lambda a: (a[0], a[1].__module__), result)
    #filter out all modules except those in harvester
    result = filter(
        lambda a: a[1].startswith('inspire.modules.harvester.workflows.'),
        result
    )
    #keep only the class name
    result = map(lambda a: a[0], result)
    return result


@manager.option('--workflow', '-w', dest='workflow')
@manager.option('--from', '-f', dest='from_date',
                help='Get records from this date and on.')
@manager.option('--to', '-t', dest='to_date',
                help='Get records until this date.')
def run(workflow, from_date, to_date):
    """Run a harvesting workflow.

    Usage: inveniomanage harvester run -w workflow_name -f 2014-01-01 -t 2014-12-31
    """
    if not workflow:
        print("Usage: inveniomanage harvester run -w workflow_name -f 2014-01-01 -t 2014-12-31")
        list_workflows()
        return
    if workflow not in get_harvesting_workflows():
        print('Invalid workflow name')
        list_workflows()
        return
    data = BibWorkflowObject.create_object()
    start_delayed(workflow, data, from_date=from_date, to_date=to_date)


@manager.command
def list_workflows():
    """List available workflows."""
    print("Available workflows:")
    for workflow in get_harvesting_workflows():
        print(workflow)
