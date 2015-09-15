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

import os
import datetime
import time

from zipfile import ZipFile

from harvestingkit.ftp_utils import FtpHandler


def get_storage_path(suffix=""):
    """Return a path ready to store files."""
    from invenio.base.globals import cfg

    storage_path = os.path.join(
        cfg.get("CFG_PREFIX"),
        cfg.get("HARVESTER_STORAGE_PREFIX"),
        suffix
    )
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path


def unzip(filename, target_folder):
    """Unzip files (XML only) into target folder."""
    z = ZipFile(filename)
    new_xml_files = []
    all_xml_files = []
    for filename in z.namelist():
        if filename.endswith(".xml"):
            absolute_path = os.path.join(target_folder, filename)
            all_xml_files.append(absolute_path)
            if not os.path.exists(absolute_path):
                z.extract(filename, target_folder)
                new_xml_files.append(absolute_path)
    return all_xml_files, new_xml_files


def ftp_download_files(server_folder, target_folder, **serverinfo):
    """Download files from given FTP's server folder to target folder."""
    ftp = FtpHandler(**serverinfo)
    ftp.cd(server_folder)
    downloaded_files = []
    all_files = []
    for filename in ftp.ls()[0]:
        destination = os.path.join(target_folder, filename)
        if not os.path.exists(destination):
            ftp.download(filename, target_folder)
            downloaded_files.append(destination)
        all_files.append(destination)
    return all_files, downloaded_files


def ftp_upload(filename, target_location=None, **serverinfo):
    """Upload files to given FTP's folder."""
    ftp = FtpHandler(**serverinfo)
    params = (filename,)
    if target_location:
        params += target_location
    ftp.upload(*params)
    ftp.close()


def validate_date(date_given, date_format="%Y-%m-%d"):
    """Return True if the date given if valid date format otherwise raise ValueError."""
    return datetime.datetime(*(time.strptime(date_given, date_format)[0:6]))
