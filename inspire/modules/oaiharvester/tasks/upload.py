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
        from invenio.modules.records.api import Record
        from inspire.modules.workflows.tasks.upload import send_robotupload

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

        marcxml = Record(obj.data.dumps()).legacy_export_as_marc()
        send_robotupload(url, marcxml, obj, eng)

    return _send_robotupload_oaiharvest
