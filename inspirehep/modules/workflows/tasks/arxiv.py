# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tasks used in OAI harvesting for arXiv record manipulation."""

from __future__ import absolute_import, print_function, unicode_literals

import os
import re

from flask import current_app

from functools import wraps

from inspirehep.utils.arxiv import (
    get_clean_arXiv_id, get_pdf, get_tarball,
)
from inspirehep.utils.helpers import (
    add_file_by_name,
    get_file_by_name,
    get_json_for_plots,
)
from inspirehep.utils.marcxml import get_json_from_marcxml
from inspirehep.modules.refextract.tasks import extract_references
from inspirehep.modules.workflows.utils import get_storage_path

from plotextractor.errors import InvalidTarball
from plotextractor.api import process_tarball
from plotextractor.converter import untar


REGEXP_AUTHLIST = re.compile(
    "<collaborationauthorlist.*?>.*?</collaborationauthorlist>", re.DOTALL)
REGEXP_REFS = re.compile(
    "<record.*?>.*?<controlfield .*?>.*?</controlfield>(.*?)</record>",
    re.DOTALL)


def arxiv_fulltext_download(doctype='arXiv'):
    """Perform the fulltext download step for arXiv records.

    :param obj: Bibworkflow Object to process
    :param eng: BibWorkflowEngine processing the object
    """
    @wraps(arxiv_fulltext_download)
    def _arxiv_fulltext_download(obj, eng):
        if "pdf" not in obj.extra_data:
            arxiv_id = get_clean_arXiv_id(obj.data)
            storage_path = get_storage_path(suffix=str(eng.uuid))

            # We download it
            pdf = get_pdf(arxiv_id, storage_path)

            if not pdf:
                obj.log.error("No arXiv pdf found!")
                return
            obj.extra_data["pdf"] = pdf
        else:
            pdf = obj.extra_data["pdf"]

        if pdf and os.path.isfile(pdf):
            if "fft" in obj.data:
                obj.data["fft"].append({
                    "url": pdf,
                    "docfile_type": doctype
                })
            else:
                new_dict_representation = {
                    "fft": [
                        {
                            "url": pdf,
                            "docfile_type": doctype
                        }
                    ]
                }
                obj.data.update(new_dict_representation)
        else:
            obj.log.error("No arXiv pdf found!")

    return _arxiv_fulltext_download


def arxiv_plot_extract(obj, eng):
    """Extract plots from an arXiv archive."""
    from wand.exceptions import DelegateError

    if "tarball" not in obj.extra_data:
        arxiv_id = get_clean_arXiv_id(obj.data)
        storage_path = get_storage_path(suffix=str(eng.uuid))

        # We download it
        tarball = get_tarball(arxiv_id, storage_path)

        if not tarball:
            obj.log.error("No arXiv tarball found!")
            return
        obj.extra_data["tarball"] = tarball
    else:
        tarball = obj.extra_data["tarball"]

    try:
        plots = process_tarball(tarball)
    except InvalidTarball:
        obj.log.error(
            'Invalid tarball {0}'.format(tarball)
        )
        return
    except DelegateError as err:
        obj.log.error("Error extracting plots. Report and skip.")
        current_app.logger.exception(err)
        return

    if plots:
        json_plots = get_json_for_plots(plots)
        obj.data.update(json_plots)
        obj.log.info("Added {0} plots.".format(len(json_plots)))


def arxiv_refextract(obj, eng):
    """Perform the reference extraction step.

    :param obj: Bibworkflow Object to process
    :param eng: BibWorkflowEngine processing the object
    """
    if "pdf" not in obj.extra_data:
        arxiv_id = get_clean_arXiv_id(obj.data)
        storage_path = get_storage_path(suffix=str(eng.uuid))

        # We download it
        pdf = get_pdf(arxiv_id, storage_path)

        if not pdf:
            obj.log.error("No arXiv pdf found!")
            return
        obj.extra_data["pdf"] = pdf
    else:
        pdf = obj.extra_data["pdf"]

    if pdf and os.path.isfile(pdf):
        mapped_references = extract_references(pdf)
        if mapped_references:
            # FIXME For now we do not add these references to the final record.
            if not current_app.config.get("PRODUCTION_MODE", False):
                obj.data["references"] = mapped_references
            else:
                obj.extra_data["references"] = mapped_references
            obj.log.info("Extracted {0} references".format(
                len(mapped_references)
            ))
        else:
            obj.log.info("No references extracted")
    else:
        obj.log.error("Not able to download and process the PDF")


def arxiv_author_list(stylesheet="authorlist2marcxml.xsl"):
    """Perform the special authorlist extraction step.

    :param obj: Bibworkflow Object to process
    :param eng: BibWorkflowEngine processing the object
    """
    @wraps(arxiv_author_list)
    def _author_list(obj, eng):
        from inspirehep.modules.converter import convert

        if "tarball" not in obj.extra_data:
            arxiv_id = get_clean_arXiv_id(obj.data)
            storage_path = get_storage_path(suffix=str(eng.uuid))

            # We download it
            tarball = get_tarball(arxiv_id, storage_path)

            if not tarball:
                obj.log.error("No arXiv tarball found!")
                return
            obj.extra_data["tarball"] = tarball
        else:
            tarball = obj.extra_data["tarball"]

        sub_dir = os.path.abspath("{0}_files".format(tarball))
        try:
            file_list = untar(tarball, sub_dir)
        except InvalidTarball:
            obj.log.error("Invalid tarball {0}".format(tarball))
            return
        obj.log.info("Extracted tarball to: {0}".format(sub_dir))

        xml_files_list = [filename for filename in file_list
                          if filename.endswith(".xml")]
        obj.log.info("Found xmlfiles: {0}".format(xml_files_list))

        for xml_file in xml_files_list:
            xml_file_fd = open(xml_file, "r")
            xml_content = xml_file_fd.read()
            xml_file_fd.close()

            match = REGEXP_AUTHLIST.findall(xml_content)
            if match:
                obj.log.info("Found a match for author extraction")
                authors_xml = convert(xml_content, stylesheet)
                authorlist_record = get_json_from_marcxml(authors_xml)[0]
                obj.data.update(authorlist_record)
                break
    return _author_list
