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

"""Implements an example of a typical ingestion workflow for MARCXML records"""

from invenio.modules.workflows.tasks.marcxml_tasks import (
    get_obj_extra_data_key,
    update_last_update
)

from invenio.modules.oaiharvester.tasks.harvesting import (
    get_repositories_list,
    init_harvesting,
    harvest_records,
)

from invenio.modules.workflows.tasks.workflows_tasks import (
    start_async_workflow,
    wait_for_a_workflow_to_complete,
    workflows_reviews,
    get_nb_workflow_created,
    get_workflows_progress,
    write_something_generic,
    num_workflow_running_greater
)

from invenio.modules.workflows.tasks.logic_tasks import (
    foreach,
    end_for,
    simple_for,
    workflow_if,
    workflow_else
)

from invenio.legacy.bibsched.bibtask import task_update_progress, write_message
from invenio.modules.workflows.definitions import WorkflowBase


class oaiharvest_production_sync(WorkflowBase):

    """Main workflow for harvesting arXiv via OAI-PMH (oaiharvester)."""

    object_type = "workflow"
    workflow = [
        write_something_generic("Initialization", [task_update_progress, write_message]),
        init_harvesting,
        write_something_generic("Starting", [task_update_progress, write_message]),
        foreach(get_repositories_list(), "repository"),
        [
            write_something_generic("Harvesting", [task_update_progress, write_message]),
            harvest_records,
            write_something_generic("Reading Files", [task_update_progress, write_message]),
            foreach(get_obj_extra_data_key("harvested_files_list")),
            [
                write_something_generic("Creating Workflows", [task_update_progress, write_message]),
                workflow_if(num_workflow_running_greater(10), neg=True),
                [
                    start_async_workflow("oaiharvest_production_sync_record",
                                         preserve_data=True,
                                         preserve_extra_data_keys=["repository"]),

                    write_something_generic(
                        ["Workflow started: ",
                         get_nb_workflow_created],
                        [task_update_progress,
                         write_message]),
                ],
                workflow_else,
                [
                    write_something_generic(
                        ["Max simultaneous workflows reached: ",
                         "Waiting for one to finish"],
                        [task_update_progress,
                         write_message]),
                    wait_for_a_workflow_to_complete(0.05),
                    start_async_workflow("oaiharvest_production_sync_record",
                                         preserve_data=True,
                                         preserve_extra_data_keys=["repository"]),
                    write_something_generic(["Workflow started :",
                                             get_nb_workflow_created,
                                             " "],
                                            [task_update_progress,
                                             write_message]),
                ],
            ],
            end_for
        ],
        end_for,
        write_something_generic(["Processing : ", get_nb_workflow_created, " records"],
                                [task_update_progress, write_message]),
        simple_for(0, get_nb_workflow_created, 1),
        [
            wait_for_a_workflow_to_complete(),
            write_something_generic([get_workflows_progress, " % Complete"],
                                    [task_update_progress, write_message]),
        ],
        end_for,
        write_something_generic("Finishing", [task_update_progress, write_message]),
        workflows_reviews(stop_if_error=True),
        update_last_update(get_repositories_list())
    ]

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        from flask import render_template

        identifiers = None

        extra_data = bwo.get_extra_data()
        if 'options' in extra_data and 'identifiers' in extra_data["options"]:
            identifiers = extra_data["options"]["identifiers"]

        results = bwo.get_tasks_results()

        if 'review_workflow' in results:
            result_progress = results['review_workflow'][0]['result']
        else:
            result_progress = {}

        current_task = extra_data['_last_task_name']

        return render_template("workflows/styles/harvesting_description.html",
                               identifiers=identifiers,
                               result_progress=result_progress,
                               current_task=current_task)

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        return "Summary of OAI harvesting from: {0}".format(
            bwo.get_extra_data()["repository"]["name"])

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        return oaiharvest_production_sync.get_description(bwo)
