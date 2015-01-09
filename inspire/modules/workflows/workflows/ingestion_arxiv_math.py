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
    get_records_from_file,
    filtering_oai_pmh_identifier
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
from invenio.modules.oaiharvester.workflows.oaiharvest_harvest_repositories import (
    oaiharvest_harvest_repositories,
)


class ingestion_arxiv_math(oaiharvest_harvest_repositories):

    """Main workflow for harvesting arXiv via OAI-PMH (oaiharvester)."""

    object_type = "workflow"
    record_workflow = "process_record_arxiv"

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
                foreach(get_records_from_file()),
                [
                    workflow_if(filtering_oai_pmh_identifier),
                    [
                        workflow_if(num_workflow_running_greater(10), neg=True),
                        [
                            start_async_workflow("process_record_arxiv",
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
                            start_async_workflow("process_record_arxiv",
                                                 preserve_data=True,
                                                 preserve_extra_data_keys=["repository"]),
                            write_something_generic(["Workflow started :",
                                                     get_nb_workflow_created,
                                                     " "],
                                                    [task_update_progress,
                                                     write_message]),
                        ],
                    ],
                ],
                end_for
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
