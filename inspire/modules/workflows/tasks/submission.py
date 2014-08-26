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

"""Contains INSPIRE specific submission tasks"""

from invenio.modules.workflows.models import BibWorkflowObject
from invenio.modules.workflows.signals import workflow_halted


def continue_workflow(sender, **extra):
    task = sender.get_current_task()
    print task
    if task == 'halt_to_render':
        sender.continue_workflow(delayed=True)

workflow_halted.connect(continue_workflow)


def halt_to_render(obj, eng):
    eng.halt("User submission complete.")


def approve_record(obj, eng):
    """Halt the workflow for approval."""
    eng.halt(action="inspire_approval",
             msg='Accept submission?')


def finalize_and_post_process(workflow_name, **kwargs):
    """Finalizes the submission and starts post-processing."""
    def _finalize_and_post_process(obj, eng):
        from invenio.modules.workflows.api import start_delayed
        from invenio.modules.workflows.models import ObjectVersion

        obj.version = ObjectVersion.FINAL
        workflow_id = start_delayed(workflow_name,
                                    data=[obj],
                                    stop_on_error=True,
                                    **kwargs)
        obj.log.info("Started new workflow ({0})".format(workflow_id))
    return _finalize_and_post_process


def send_robotupload(url):
    """Gets the MARCXML from the deposit object and ships it."""

    def _send_robotupload(obj, eng):
        from invenio.modules.deposit.models import Deposition
        from inspire.utils.robotupload import make_robotupload_marcxml

        d = Deposition(obj)
        sip = d.get_latest_sip(sealed=False)
        sip.seal()

        result = make_robotupload_marcxml(
            url=url,
            marcxml=sip.package
        )
        if not "[INFO]" in result.text:
            if "cannot use the service" in result.text:
                # IP not in the list
                obj.log.error("Your IP is not in CFG_BATCHUPLOADER_WEB_ROBOT_RIGHTS on host")
                obj.log.error(result.text)
            from invenio.modules.workflows.errors import WorkflowError
            txt = "Error while submitting robotupload: {0}".format(result.text)
            raise WorkflowError(txt, eng.uuid, obj.id)
        else:
            obj.log.info("Robotupload sent!")
            obj.log.info(result.text)
    return _send_robotupload

