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
    basename
)
from datetime import datetime

from harvestingkit.world_scientific_package import WorldScientific
from zipfile import BadZipfile

from inspire.modules.harvester.utils import (
    unzip,
    make_collection,
    ftp_upload,
    ftp_download_files,
)

from ..config import (
    CFG_WS_DOWNLOAD_FOLDER,
    CFG_WS_EXTRACT_FOLDER,
    CFG_WS_MARC_FOLDER,
    CFG_WS_FOLDER_ON_SERVER,
    CFG_DESY_FTP_SERVER,
    CFG_DESY_NETRC_FILE
)


def get_files(obj, eng):
    obj.extra_data['downloaded_files'] = ftp_download_files(
        CFG_WS_FOLDER_ON_SERVER,
        CFG_WS_DOWNLOAD_FOLDER,
        server=CFG_DESY_FTP_SERVER,
        netrc_file=CFG_DESY_NETRC_FILE,
    )


def unzip_file(obj, eng):
    filenames = obj.extra_data['downloaded_files']
    extracted_files = []
    for filename in filenames:
        try:
            extracted_files.extend(unzip(filename, CFG_WS_EXTRACT_FOLDER))
        except BadZipfile:
            pass
    obj.extra_data['extracted_files'] = extracted_files


def convert_files(obj, eng):
    from invenio.modules.knowledge.api import get_kb_mappings
    mappings = dict(
        map(
            lambda item: (item['key'], item['value']),
            get_kb_mappings('JOURNALS')
        )
    )
    filenames = obj.extra_data['extracted_files']

    ws = WorldScientific(mappings)
    append_files = []
    insert_files = []
    from_date = eng.extra_data['from_date']
    to_date = eng.extra_data['to_date']
    if not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
    if not from_date:
        from_date = ''
    for filename in filenames:
        date = ws.get_date(filename)
        if from_date <= date <= to_date:
            marc = ws.get_record(filename)
            if marc:
                filename = basename(filename)
                filename = join(CFG_WS_MARC_FOLDER, filename)
                if ws._get_article_type() in ['research-article',
                                              'introduction',
                                              'letter']:
                    insert_files.append(filename)
                elif ws._get_article_type() in ['correction',
                                                'addendum']:
                    append_files.append(filename)
                with open(filename, 'w') as outfile:
                    outfile.write(marc)
    obj.extra_data['append'] = append_files
    obj.extra_data['insert'] = insert_files


def upload_to_desy(obj, eng):
    collections = obj.extra_data['collections']
    for filename in collections:
        ftp_upload(
            filename,
            server=CFG_DESY_FTP_SERVER,
            netrc_file=CFG_DESY_NETRC_FILE,
        )


def create_collection(obj, eng):
    append_files = obj.extra_data['append']
    insert_files = obj.extra_data['insert']
    date = datetime.now().strftime("%Y.%m.%d")
    insert_file = "world_scientific-%s.insert.xml" % date
    insert_file = join(CFG_WS_MARC_FOLDER, insert_file)
    append_file = "world_scientific-%s.append.xml" % date
    append_file = join(CFG_WS_MARC_FOLDER, append_file)
    obj.extra_data['collections'] = []
    if insert_files:
        make_collection(insert_files, insert_file, logger=obj.log)
        obj.extra_data['collections'].append(insert_file)
    if append_files:
        make_collection(append_files, append_file, logger=obj.log)
        obj.extra_data['collections'].append(append_file)
