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


def send_robotupload(url, marcxml, obj, eng):
    """Ships the marcxml to url."""
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
