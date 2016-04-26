# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tasks used in OAI harvesting for arXiv record manipulation."""

from __future__ import absolute_import, print_function, unicode_literals

import os
import re

from flask import current_app

from functools import wraps

from inspirehep.utils.arxiv import (
    get_arxiv_id_from_record, get_pdf, get_tarball,
)
from inspirehep.utils.helpers import (
    add_file_by_name,
    get_file_by_name,
    get_json_for_plots,
)
from inspirehep.utils.marcxml import get_json_from_marcxml

from inspirehep.modules.refextract.tasks import extract_references

from invenio_base.globals import cfg

from plotextractor.errors import InvalidTarball
from plotextractor.api import process_tarball
from plotextractor.converter import untar


REGEXP_AUTHLIST = re.compile(
    "<collaborationauthorlist.*?>.*?</collaborationauthorlist>", re.DOTALL)
REGEXP_REFS = re.compile(
    "<record.*?>.*?<controlfield .*?>.*?</controlfield>(.*?)</record>",
    re.DOTALL)


def get_pdf_for_model(eng, arxiv_id):
    """We download it."""
    storage_path = os.path.join(
        cfg.get('WORKFLOWS_STORAGEDIR', cfg.get('CFG_TMPSHAREDDIR')),
        str(eng.uuid)
    )
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return get_pdf(
        arxiv_id,
        storage_path
    )


def get_tarball_for_model(eng, arxiv_id):
    """We download it."""
    storage_path = os.path.join(
        cfg.get('WORKFLOWS_STORAGEDIR', cfg.get('CFG_TMPSHAREDDIR')),
        str(eng.uuid)
    )
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return get_tarball(
        arxiv_id,
        storage_path
    )


def arxiv_fulltext_download(doctype='arXiv'):
    """Perform the fulltext download step for arXiv records.

    :param obj: Bibworkflow Object to process
    :param eng: BibWorkflowEngine processing the object
    """
    @wraps(arxiv_fulltext_download)
    def _arxiv_fulltext_download(obj, eng):
        arxiv_id = get_arxiv_id_from_record(obj.data)
        existing_file = get_file_by_name(model, "{0}.pdf".format(arxiv_id))

        if not existing_file:
            # We download it
            pdf = get_pdf_for_model(eng, arxiv_id)

            if pdf is None:
                obj.log.error("No pdf found")
                return
            pdf = add_file_by_name(model, pdf)
            obj.extra_data["pdf"] = pdf
        else:
            pdf = existing_file.get_syspath()

        if pdf:
            if "fft" in record:
                record["fft"].append({
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
                record.update(new_dict_representation)

            fileinfo = {
                "type": "fulltext",
                "filename": os.path.basename(pdf),
                "full_path": pdf,
            }
            obj.update_task_results(
                os.path.basename(pdf),
                [{
                    "name": "PDF",
                    "result": fileinfo,
                    "template": "workflows/results/files.html"
                }]
            )
            model.update()
        else:
            obj.log.info("No PDF found.")

    return _arxiv_fulltext_download


def arxiv_plot_extract(obj, eng):
    """Extract plots from an arXiv archive."""
    from wand.exceptions import DelegateError

    arxiv_id = get_arxiv_id_from_record(obj.data)
    existing_file = get_file_by_name(model, "{0}.tar.gz".format(arxiv_id))

    if not existing_file:
        # We download it
        tarball = get_tarball_for_model(eng, arxiv_id)

        if tarball is None:
            obj.log.error("No tarball found")
            return
        add_file_by_name(model, tarball)
    else:
        tarball = existing_file.get_syspath()

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
        # We store the path to the directory the tarball contents lives
        json_plots = get_json_for_plots(plots)
        obj.data.update(json_plots)
        obj.update_task_results(
            "Plots",
            [{
                "name": "Plots",
                "result": new_dict["fft"],
                "template": "workflows/results/plots.html"
            }]
        )
        obj.log.info("Added {0} plots.".format(len(new_dict["fft"])))
        model.update()


def arxiv_refextract(obj, eng):
    """Perform the reference extraction step.

    :param obj: Bibworkflow Object to process
    :param eng: BibWorkflowEngine processing the object
    """
    arxiv_id = get_arxiv_id_from_record(obj.data)
    existing_file = get_file_by_name(model, "{0}.pdf".format(arxiv_id))

    if not existing_file:
        # We download it
        pdf = get_pdf_for_model(eng, arxiv_id)

        if pdf is None:
            obj.log.error("No pdf found")
            return
        add_file_by_name(model, pdf)
    else:
        pdf = existing_file.get_syspath()

    if pdf and os.path.isfile(pdf):
        mapped_references = extract_references(pdf)
        if mapped_references:
            # FIXME For now we do not add these references to the final record.
            if not current_app.config.get("PRODUCTION_MODE", False):
                record["references"] = mapped_references
            obj.log.info("Extracted {0} references".format(
                len(mapped_references)
            ))
            obj.update_task_results(
                "References",
                [{"name": "References",
                  "result": mapped_references,
                  "template": "workflows/results/refextract.html"}]
            )
            model.update()
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
        from inspirehep.modules.converter.xslt import convert

        arxiv_id = get_arxiv_id_from_record(obj.data)
        existing_file = get_file_by_name(model, "{0}.tar.gz".format(arxiv_id))

        if not existing_file:
            # We download it
            tarball = get_tarball_for_model(eng, arxiv_id)

            if tarball is None:
                obj.log.error("No tarball found")
                return
            add_file_by_name(model, tarball)
        else:
            tarball = existing_file.get_syspath()

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
                record.update(authorlist_record)
                obj.update_task_results(
                    "authors",
                    [{
                        "name": "authors",
                        "results": authorlist_record["authors"]
                    }]
                )
                obj.update_task_results(
                    "number_of_authors",
                    [{
                        "name": "number_of_authors",
                        "results": authorlist_record["number_of_authors"]
                    }]
                )
                break
        model.update()
    return _author_list
