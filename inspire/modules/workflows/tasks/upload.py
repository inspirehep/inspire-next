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


def send_robotupload(url, marcxml, obj, eng):
    """Ship the marcxml to url."""
    from invenio.base.globals import cfg
    from inspire.utils.robotupload import make_robotupload_marcxml

    if url is None:
        base_url = cfg.get("CFG_ROBOTUPLOAD_SUBMISSION_BASEURL")
    else:
        base_url = url

    callback_url = os.path.join(cfg["CFG_SITE_URL"],
                                "callback/workflows/robotupload")
    obj.log.info("Sending Robotupload to {0} with callback {1}".format(
        base_url,
        callback_url
    ))

    result = make_robotupload_marcxml(
        obj=obj,
        eng=eng,
        url=base_url,
        marcxml=marcxml,
        callback_url=callback_url,
        nonce=obj.id
    )
    if "[INFO]" not in result.text:
        if "cannot use the service" in result.text:
            # IP not in the list
            obj.log.error("Your IP is not in "
                          "CFG_BATCHUPLOADER_WEB_ROBOT_RIGHTS "
                          "on host")
            obj.log.error(result.text)
        from invenio.modules.workflows.errors import WorkflowError
        txt = "Error while submitting robotupload: {0}".format(result.text)
        raise WorkflowError(txt, eng.uuid, obj.id)
    else:
        obj.log.info("Robotupload sent!")
        obj.log.info(result.text)
        eng.halt("Waiting for robotupload: {0}".format(result.text))
    obj.log.info("end of upload")


def upload_step_marcxml(obj, eng):
    """Perform the upload step with MARCXML in obj.data().

    :param obj: BibWorkflowObject to process
    :param eng: BibWorkflowEngine processing the object
    """
    from invenio.base.globals import cfg
    from invenio.legacy.oaiharvest.dblayer import create_oaiharvest_log_str
    from invenio.legacy.bibsched.bibtask import task_low_level_submission

    sequence_id = random.randrange(1, 60000)

    arguments = obj.extra_data["repository"]["arguments"]

    default_args = []
    default_args.extend(['-I', str(sequence_id)])
    if arguments.get('u_name', ""):
        default_args.extend(['-N', arguments.get('u_name', "")])
    if arguments.get('u_priority', 5):
        default_args.extend(['-P', str(arguments.get('u_priority', 5))])
    arguments = obj.extra_data["repository"]["arguments"]

    extract_path = os.path.join(
        cfg['CFG_TMPSHAREDDIR'],
        str(eng.uuid)
    )
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    filepath = extract_path + os.sep + str(obj.id)
    if "f" in obj.extra_data["repository"]["postprocess"]:
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
                create_oaiharvest_log_str(task_id,
                                          obj.extra_data["repository"]["id"],
                                          obj.get_data())
            except Exception as msg:
                eng.log.error(
                    "An exception during submitting oaiharvest task occured : %s " % (
                        str(msg)))
    if task_id is None:
        eng.log.error("an error occurred while uploading %s from %s" %
                      (filepath, obj.extra_data["repository"]["name"]))
    else:
        eng.log.info(
            "material harvested from source %s was successfully uploaded" %
            (obj.extra_data["repository"]["name"],))
    eng.log.info("end of upload")
