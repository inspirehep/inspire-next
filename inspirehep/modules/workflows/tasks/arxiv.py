# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tasks used in OAI harvesting for arXiv record manipulation."""

from __future__ import absolute_import, division, print_function

import os
import re
from functools import wraps

from flask import current_app
from six import BytesIO
from werkzeug import secure_filename

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hep import hep
from inspirehep.modules.refextract.tasks import extract_references
from inspirehep.utils.arxiv import get_clean_arXiv_id
from inspirehep.utils.helpers import download_file_to_record

from plotextractor.api import process_tarball
from plotextractor.converter import untar
from plotextractor.errors import InvalidTarball, NoTexFilesFound


REGEXP_AUTHLIST = re.compile(
    "<collaborationauthorlist.*?>.*?</collaborationauthorlist>", re.DOTALL)
REGEXP_REFS = re.compile(
    "<record.*?>.*?<controlfield .*?>.*?</controlfield>(.*?)</record>",
    re.DOTALL)


def arxiv_fulltext_download(obj, eng):
    """Perform the fulltext download step for arXiv records.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    arxiv_id = get_clean_arXiv_id(obj.data)
    filename = secure_filename("{0}.pdf".format(arxiv_id))
    if filename not in obj.files:
        pdf = download_file_to_record(
            record=obj,
            name=filename,
            url=current_app.config['ARXIV_PDF_URL'].format(
                arxiv_id=arxiv_id
            )
        )
        pdf['doctype'] = "arXiv"


def arxiv_plot_extract(obj, eng):
    """Extract plots from an arXiv archive.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    from wand.exceptions import DelegateError

    arxiv_id = get_clean_arXiv_id(obj.data)
    filename = secure_filename("{0}.tar.gz".format(arxiv_id))
    if filename not in obj.files:
        tarball = download_file_to_record(
            record=obj,
            name=filename,
            url=current_app.config['ARXIV_TARBALL_URL'].format(
                arxiv_id=arxiv_id
            )
        )
    else:
        tarball = obj.files[filename]

    try:
        plots = process_tarball(tarball.file.uri)
    except (InvalidTarball, NoTexFilesFound):
        obj.log.error(
            'Invalid tarball {0}'.format(tarball.file.uri)
        )
        return
    except DelegateError as err:
        obj.log.error("Error extracting plots. Report and skip.")
        current_app.logger.exception(err)
        return

    for idx, plot in enumerate(plots):
        obj.files[plot.get('name')] = BytesIO(open(plot.get('url')))
        obj.files[plot.get('name')]["doctype"] = "Plot"
        obj.files[plot.get('name')]["description"] = "{0:05d} {1}".format(
            idx, "".join(plot.get('captions', []))
        )
    obj.log.info("Added {0} plots.".format(len(plots)))


def arxiv_refextract(obj, eng):
    """Extract references from arXiv PDF.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    arxiv_id = get_clean_arXiv_id(obj.data)
    filename = secure_filename("{0}.pdf".format(arxiv_id))
    if filename not in obj.files:
        pdf = download_file_to_record(
            record=obj,
            name=filename,
            url=current_app.config['ARXIV_PDF_URL'].format(
                arxiv_id=arxiv_id
            )
        )
    else:
        pdf = obj.files[filename]
    if pdf:
        mapped_references = extract_references(pdf.file.uri)
        if mapped_references:
            obj.data["references"] = mapped_references
            obj.log.info("Extracted {0} references".format(
                len(mapped_references)
            ))
        else:
            obj.log.info("No references extracted")
    else:
        obj.log.error("Not able to download and process the PDF")


def arxiv_author_list(stylesheet="authorlist2marcxml.xsl"):
    """Extract authors from any author XML found in the arXiv archive.

    :param obj: Workflow Object to process
    :param eng: Workflow Engine processing the object
    """
    @wraps(arxiv_author_list)
    def _author_list(obj, eng):
        from inspirehep.modules.converter import convert

        arxiv_id = get_clean_arXiv_id(obj.data)
        filename = secure_filename("{0}.tar.gz".format(arxiv_id))
        if filename not in obj.files:
            tarball = download_file_to_record(
                record=obj,
                name=filename,
                url=current_app.config['ARXIV_TARBALL_URL'].format(
                    arxiv_id=arxiv_id
                )
            )
        else:
            tarball = obj.files[filename]

        sub_dir = os.path.abspath("{0}_files".format(tarball.file.uri))
        try:
            file_list = untar(tarball.file.uri, sub_dir)
        except InvalidTarball:
            obj.log.error("Invalid tarball {0}".format(tarball.file.uri))
            return
        obj.log.info("Extracted tarball to: {0}".format(sub_dir))

        xml_files_list = [path for path in file_list
                          if path.endswith(".xml")]
        obj.log.info("Found xmlfiles: {0}".format(xml_files_list))

        for xml_file in xml_files_list:
            xml_file_fd = open(xml_file, "r")
            xml_content = xml_file_fd.read()
            xml_file_fd.close()

            match = REGEXP_AUTHLIST.findall(xml_content)
            if match:
                obj.log.info("Found a match for author extraction")
                authors_xml = convert(xml_content, stylesheet)
                authors_rec = create_record(authors_xml)
                authorlist_record = hep.do(authors_rec)
                obj.data.update(authorlist_record)
                break
    return _author_list
