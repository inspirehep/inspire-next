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

import os
import random


def upload_step_marcxml(obj, eng):
    """Perform the upload step with MARCXML in obj.data().

    :param obj: BibWorkflowObject to process
    :param eng: BibWorkflowEngine processing the object
    """
    from invenio.base.globals import cfg
    from invenio.legacy.oaiharvest.dblayer import create_oaiharvest_log_str
    from invenio.legacy.bibsched.bibtask import task_low_level_submission

    repository = obj.extra_data.get("repository", {})
    sequence_id = random.randrange(1, 60000)

    arguments = repository.get("arguments", {})

    default_args = []
    default_args.extend(['-I', str(sequence_id)])
    if arguments.get('u_name', ""):
        default_args.extend(['-N', arguments.get('u_name', "")])
    if arguments.get('u_priority', 5):
        default_args.extend(['-P', str(arguments.get('u_priority', 5))])

    extract_path = os.path.join(
        cfg['CFG_TMPSHAREDDIR'],
        str(eng.uuid)
    )
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    filepath = extract_path + os.sep + str(obj.id)
    if "f" in repository.get("postprocess", []):
        # We have a filter.
        file_uploads = [
            ("{0}.insert.xml".format(filepath), ["-i"]),
            ("{0}.append.xml".format(filepath), ["-a"]),
            ("{0}.correct.xml".format(filepath), ["-c"]),
            ("{0}.holdingpen.xml".format(filepath), ["-o"]),
        ]
    else:
        # We do not, so we get the data from the record
        file_fd = open(filepath, 'w')
        file_fd.write(obj.get_data())
        file_fd.close()
        file_uploads = [(filepath, ["-r", "-i"])]

    task_id = None
    for location, mode in file_uploads:
        if os.path.exists(location):
            try:
                args = mode + [filepath] + default_args
                task_id = task_low_level_submission("bibupload",
                                                    "oaiharvest",
                                                    *tuple(args))
                repo_id = repository.get("id")
                if repo_id:
                    create_oaiharvest_log_str(
                        task_id,
                        repo_id,
                        obj.get_data()
                    )
            except Exception as msg:
                eng.log.error(
                    "An exception during submitting OAI harvester task occurred: %s " % (
                        str(msg)))
    if task_id is None:
        eng.log.error("an error occurred while uploading %s from %s" %
                      (filepath, repository.get("name", "Unknown")))
    else:
        eng.log.info(
            "material harvested from source %s was successfully uploaded" %
            (repository.get("name", "Unknown"),))
    eng.log.info("end of upload")
