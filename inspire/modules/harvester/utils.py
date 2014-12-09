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

from os.path import (
    join,
    exists
)

from zipfile import ZipFile
from harvestingkit.ftp_utils import FtpHandler


def unzip(filename, target_folder):
    z = ZipFile(filename)
    xml_files_extracted = []
    for filename in z.namelist():
        if filename.endswith(".xml"):
            absolute_path = join(target_folder, filename)
            xml_files_extracted.append(absolute_path)
            if not exists(absolute_path):
                z.extract(filename, target_folder)
    return xml_files_extracted


def make_collection(filelist, location, logger=None):
    with open(location, 'w') as outfile:
        outfile.write('<collection>\n')
        for filename in filelist:
            try:
                infile = open(filename)
                outfile.write(infile.read())
            except IOError:
                if logger:
                    logger.error('Unable to locate the file %s' % filename)
            finally:
                infile.close()
        outfile.write('\n</collection>')


def ftp_download_files(server_folder, target_folder, **serverinfo):
    ftp = FtpHandler(**serverinfo)
    ftp.cd(server_folder)
    downloaded_files = []
    for filename in ftp.ls()[0]:
        destination = join(target_folder, filename)
        if not exists(destination):
            ftp.download(filename, target_folder)
            downloaded_files.append(destination)
    return downloaded_files


def ftp_upload(filename, target_location=None, **serverinfo):
    ftp = FtpHandler(**serverinfo)
    params = (filename,)
    if target_location:
        params += target_location
    ftp.upload(*params)
    ftp.close()
