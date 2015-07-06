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

import random
import os
from functools import wraps
from invenio.base.globals import cfg


def send_robotupload_oaiharvest(url=None):
    """Perform the upload step."""
    @wraps(send_robotupload_oaiharvest)
    def _send_robotupload_oaiharvest(obj, eng):
        from invenio_records.api import Record
        from inspire.utils.robotupload import make_robotupload_marcxml

        sequence_id = random.randrange(1, 60000)

        arguments = obj.extra_data.get("repository", {}).get("arguments", {})

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

        callback_url = os.path.join(cfg["CFG_SITE_URL"],
                                    "callback/workflows/continue")

        marcxml = Record(obj.data.dumps()).legacy_export_as_marc()
        result = make_robotupload_marcxml(
            url=url,
            marcxml=marcxml,
            callback_url=callback_url,
            mode='insert',
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

    return _send_robotupload_oaiharvest


def update_existing_record_oaiharvest(url=None):
    """Update the existing record on the remote site."""
    @wraps(update_existing_record_oaiharvest)
    def _update(obj, eng):
        import dictdiffer

        from lxml import objectify, etree

        from invenio.base.globals import cfg
        from invenio.modules.workflows.utils import convert_marcxml_to_bibfield
        from invenio_records.api import Record

        from inspire.utils.robotupload import make_robotupload_marcxml

        try:
            recid = obj.extra_data["recid"]
        except KeyError:
            obj.log.error("Cannot locate record ID")
            return

        callback_url = os.path.join(cfg["CFG_SITE_URL"],
                                    "callback/workflows/continue")

        search_url = "%s?p=recid:%s&of=xm" % (cfg["WORKFLOWS_MATCH_REMOTE_SERVER_URL"], recid)

        prod_data = objectify.parse(search_url)
        # remove controlfields
        root = prod_data.getroot()
        record = root['record']
        while True:
            try:
                record.remove(record['controlfield'])
            except AttributeError:
                break
        prod_data = etree.tostring(record)
        prod_data = convert_marcxml_to_bibfield(prod_data, model=["hep"])
        new_data = dict(obj.data.dumps(clean=True))
        prod_data = dict(prod_data.dumps(clean=True))
        updated_keys = []
        diff = dictdiffer.diff(prod_data, new_data)
        for diff_type, new_key, content in diff:
            if diff_type == 'add':
                if new_key:
                    if isinstance(new_key, list):
                        # ['subject_term', 0]
                        updated_keys.append(new_key[0])
                    else:
                        # 'subject_term'
                        updated_keys.append(new_key)
                else:
                    # content must be list of new adds
                    for key in content:
                        updated_keys.append(key)

        updates = dictdiffer.patch(diff, new_data)
        for key in updates.keys():
            if key not in updated_keys:
                del updates[key]
        if updates:
            updates['recid'] = recid
            marcxml = Record(updates).legacy_export_as_marc()
            result = make_robotupload_marcxml(
                url=url,
                marcxml=marcxml,
                callback_url=callback_url,
                mode='correct',
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
        else:
            obj.log.info("No updates to do.")

    return _update
