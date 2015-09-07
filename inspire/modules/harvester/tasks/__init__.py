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

from invenio.celery import celery


@celery.task()
def run_harvest(workflow, **kwargs):
    """Run given harvesting workflow in Celery."""
    from invenio.base.globals import cfg
    from invenio_workflows.models import BibWorkflowObject

    args = {
        "workflow": workflow
    }
    args.update(**kwargs)

    data = BibWorkflowObject.create_object()
    extra_data = data.get_extra_data()
    extra_data["args"] = args
    extra_data["config"] = cfg["HARVESTER_WORKFLOWS_CONFIG"].get(workflow, {})
    data.set_extra_data(extra_data)
    data.set_data({})
    data.save()
    data.start_workflow(workflow, delayed=True)
