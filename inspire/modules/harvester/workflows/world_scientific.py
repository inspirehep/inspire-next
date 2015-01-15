# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
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

"""World Scientific harvesting workflow."""

from ..definitions import HarvestingWorkflowBase

from ..tasks.world_scientific import (
    get_files_from_ftp,
    unzip_files,
    convert_files,
    create_collection,
    put_files_to_ftp,
    report_via_email
)


class world_scientific(HarvestingWorkflowBase):

    """Harvest and convert World Scientific articles from FTP."""

    object_type = "workflow"
    ftp_server = "ftp.desy.de"
    report_recipients = [
        "kirsten.sachs@desy.de",
        "florian.schwennsen@desy.de",
        "jan.age.lavik@cern.ch"
    ]

    workflow = [
        get_files_from_ftp(
            server=ftp_server,
            source_folder='WSP',
            target_folder='worldscientific/ws_download'
        ),
        unzip_files('worldscientific/ws_extracted'),
        convert_files('worldscientific/ws_marc'),
        create_collection,
        put_files_to_ftp(
            server=ftp_server,
        ),
        report_via_email(
            recipients=report_recipients,
            template="harvester/ftp_upload_notification.html"
        ),
    ]
