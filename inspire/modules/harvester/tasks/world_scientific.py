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

from os.path import (
    join,
    basename,
)

from functools import wraps
from datetime import datetime, timedelta
from zipfile import BadZipfile
from shutil import move
from flask import render_template

from harvestingkit.world_scientific_package import WorldScientific

from invenio.ext.email import send_email
from invenio.base.globals import cfg

from inspire.modules.harvester.utils import (
    unzip,
    ftp_upload,
    ftp_download_files,
    get_storage_path,
)


def get_files_from_ftp(source_folder, target_folder):
    """Get all files in given folder on FTP server to target folder.

    The paths to the retrieved files are put in data["downloaded_files"].
    """
    @wraps(get_files_from_ftp)
    def _get_files_from_ftp(obj, eng):
        netrc_file = obj.extra_data["config"].get("ftp_netrc_file")
        target_folder_full = get_storage_path(suffix=target_folder)
        obj.data['all_files'], obj.data['new_files'] = ftp_download_files(
            source_folder,
            target_folder_full,
            server=obj.extra_data["config"]["ftp_server"],
            netrc_file=netrc_file
        )
        obj.log.info("{0} new files downloaded, in total {1} files".format(
            len(obj.data["new_files"]),
            len(obj.data["all_files"])
        ))
    return _get_files_from_ftp


def unzip_files(target_folder):
    """Unzip new files to target location.

    All extracted files are stored in data["all_extracted_files"] and
    data["newly_extracted_files"].
    """
    @wraps(unzip_files)
    def _unzip_files(obj, eng):
        target_folder_full = get_storage_path(suffix=target_folder)
        filenames = obj.data.get('all_files', list())
        all_extracted_files = []
        newly_extracted_files = []
        for filename in filenames:
            try:
                all_extracted, new_extracted = unzip(filename,
                                                     target_folder_full)
                all_extracted_files.extend(all_extracted)
                newly_extracted_files.extend(new_extracted)
            except BadZipfile as e:
                obj.log.error("Error unzipping file {0}: {1}".format(
                    filename,
                    e
                ))
                pass
        obj.data['all_extracted_files'] = all_extracted_files
        obj.data['newly_extracted_files'] = newly_extracted_files
        obj.log.debug("{0} new files extracted".format(
            len(obj.data["newly_extracted_files"])
        ))

    return _unzip_files


def convert_files(target_folder, weeks_threshold=30):
    """Convert appropriate files in data to MARCXML."""
    @wraps(convert_files)
    def _convert_files(obj, eng):
        from invenio_knowledge.api import get_kb_mappings
        mappings = dict(
            map(
                lambda item: (item['key'], item['value']),
                get_kb_mappings('JOURNALS')
            )
        )
        ws = WorldScientific(mappings)

        target_folder_full = get_storage_path(suffix=target_folder)

        args = obj.extra_data['args']

        # By default, we set the from date as today
        to_date = args.get("to_date") or datetime.now().strftime('%Y-%m-%d')

        # By last resort, we set the from date months before
        from_date = args.get("from_date")

        if not from_date:
            if args.get("reharvest"):
                # Since "beginning" of time when not specified
                from_date = datetime.strptime("1900-01-01", "%Y-%m-%d")
            else:
                # Dynamic date in the past when not specified and not reharvest
                from_date = datetime.now() - timedelta(weeks=weeks_threshold)\
                    .strftime('%Y-%m-%d')

        obj.extra_data['args']["to_date"] = to_date
        obj.extra_data['args']["from_date"] = from_date

        insert_files = []
        if args.get("reharvest"):
            filenames = obj.data['all_extracted_files']
        else:
            filenames = obj.data['newly_extracted_files']

        for filename in filenames:
            date = ws.get_date(filename)
            if date is None or (from_date <= date <= to_date):
                marc = ws.get_record(filename)
                if marc:
                    filename = basename(filename)
                    filename = join(target_folder_full, filename)
                    insert_files.append(filename)
                    with open(filename, 'w') as outfile:
                        outfile.write(marc)
            else:
                obj.log.info("Filtered out {0} ({1})".format(filename, date))

        obj.log.info("Converted {0}/{1} articles between {2} to {3}".format(
            len(insert_files),
            len(filenames),
            from_date,
            to_date
        ))

        obj.data['insert'] = insert_files
        obj.data["result_path"] = target_folder_full

        obj.log.debug("Saved converted files to {0}".format(target_folder_full))
        obj.log.debug("{0} files to add".format(
            len(obj.data["insert"]),
        ))
    return _convert_files


def create_collection(obj, eng):
    """Squash all the insert records into batch collections."""
    args = obj.extra_data['args']
    to_date = args.get("to_date") or datetime.now().strftime('%Y-%m-%d')
    from_date = args.get("from_date")
    date = "_".join([d for d in [from_date, to_date] if d])
    obj.data['collections'] = {}

    prefix_path = ""
    if not obj.data.get("result_path"):
        prefix_path = join(
            cfg.get("HARVESTER_STORAGE_PREFIX"),
            "worldscientific"
        )
    else:
        prefix_path = obj.data.get("result_path")

    final_filename = join(
        prefix_path,
        "world_scientific-{0}.{1}.xml".format(date, "insert")
    )

    files = obj.data.get("insert", list())
    if files:
        with open(final_filename, 'w') as outfile:
            outfile.write('<collection>\n')
            for filename in files:
                try:
                    infile = open(filename)
                    outfile.write(infile.read())
                except IOError:
                    obj.log.error('Unable to locate the file {0}'.format(
                        filename
                    ))
                finally:
                    infile.close()
            outfile.write('\n</collection>')
        obj.data['collections'].update({"insert": final_filename})
    obj.log.debug("{0} files ready for upload:\n{1}".format(
        len(obj.data["collections"]),
        "\n".join([f for f in obj.data["collections"].values()])
    ))


def put_files_to_ftp(obj, eng):
    """Upload files in data["collections"] to given FTP server."""
    collections = obj.data.get('collections', dict())
    server = obj.extra_data["config"]["ftp_server"]
    netrc_file = obj.extra_data["config"].get("ftp_netrc_file")
    for filename in collections.values():
        if cfg.get("PRODUCTION_MODE"):
            ftp_upload(
                filename,
                server=server,
                netrc_file=netrc_file,
            )
            obj.log.info("Uploaded {0} to {1}".format(filename, server))
        else:
            obj.log.info("(pretend) Uploaded to {0} to {1}".format(
                filename,
                server)
            )


def move_to_done(target_folder):
    """Upload files in data["collections"] to given FTP server."""
    @wraps(put_files_to_ftp)
    def _move_to_done(obj, eng):
        target_folder_full = get_storage_path(suffix=target_folder)
        collections = obj.data.get('collections', dict())
        for filename in collections.values():
            move(filename, join(target_folder_full, basename(filename)))
            obj.log.info("Moved {0} to {1}".format(
                filename,
                target_folder_full)
            )
    return _move_to_done


def report_via_email(template=None):
    """Report about completed uploads to recipients."""
    @wraps(report_via_email)
    def _report_via_email(obj, eng):
        recipients = obj.extra_data["config"].get("recipients")
        if not recipients:
            obj.log.warning("No recipients")
            return

        collections = obj.data.get('collections', dict())
        files_uploaded = []
        for update_type, filename in collections.items():
            count = len(obj.data.get(update_type, list()))
            files_uploaded.append((basename(filename), count))

        harvesting_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = {
            "object": obj,
            "files_uploaded": files_uploaded,
            "args": obj.extra_data.get("args", dict()),
            "harvesting_date": harvesting_date
        }

        body = render_template(
            template,
            **context
        )
        subject = "{0} harvest results: {1}".format(
            context.get("args").get("workflow"),
            harvesting_date
        )

        send_email(fromaddr=cfg.get("CFG_SITE_SUPPORT_EMAIL"),
                   toaddr=recipients,
                   subject=subject,
                   content=body)

    return _report_via_email
