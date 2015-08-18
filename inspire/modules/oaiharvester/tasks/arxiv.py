# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
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

from functools import wraps

from invenio.base.globals import cfg

from invenio.utils.shell import Timeout

from invenio.utils.plotextractor.api import (
    get_tarball_from_arxiv,
    get_marcxml_plots_from_tarball,
    get_pdf_from_arxiv,
)
from inspire.utils.helpers import (
    get_record_from_model,
    add_file_by_name,
    get_file_by_name,
)
from inspire.utils.marcxml import get_json_from_marcxml


REGEXP_AUTHLIST = re.compile(
    "<collaborationauthorlist.*?>.*?</collaborationauthorlist>", re.DOTALL)
REGEXP_REFS = re.compile(
    "<record.*?>.*?<controlfield .*?>.*?</controlfield>(.*?)</record>",
    re.DOTALL)


def get_arxiv_id_from_record(record):
    """Return the arXiv identifier from given record.

    This function works with Deposition and Payload data models.
    """
    arxiv_id = record.get("arxiv_id")
    if not arxiv_id:
        report_numbers = record.get('report_number', [])
        for number in report_numbers:
            if number.get("source", "").lower() == "arxiv":
                arxiv_id = number.get("primary")

    if not arxiv_id.startswith("arXiv"):
        arxiv_id = "arXiv:{0}".format(arxiv_id)
    return arxiv_id


def arxiv_fulltext_download(doctype='arXiv'):
    @wraps(arxiv_fulltext_download)
    def _arxiv_fulltext_download(obj, eng):
        """Perform the fulltext download step for arXiv records.

        :param obj: Bibworkflow Object to process
        :param eng: BibWorkflowEngine processing the object
        """
        model = eng.workflow_definition.model(obj)
        record = get_record_from_model(model)
        arxiv_id = get_arxiv_id_from_record(record)
        existing_file = get_file_by_name(model, "{0}.pdf".format(arxiv_id))

        if not existing_file:
            # We download it
            extract_path = os.path.join(
                cfg.get('OAIHARVESTER_STORAGEDIR', cfg.get('CFG_TMPSHAREDDIR')),
                str(eng.uuid)
            )

            pdf = get_pdf_from_arxiv(
                arxiv_id,
                extract_path
            )

            if pdf is None:
                obj.log.error("No pdf found")
                return
            add_file_by_name(model, pdf)
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
    model = eng.workflow_definition.model(obj)
    record = get_record_from_model(model)
    arxiv_id = get_arxiv_id_from_record(record)
    existing_file = get_file_by_name(model, arxiv_id)

    if not existing_file:
        # We download it
        extract_path = os.path.join(
            cfg.get('OAIHARVESTER_STORAGEDIR', cfg.get('CFG_TMPSHAREDDIR')),
            str(eng.uuid)
        )

        tarball = get_tarball_from_arxiv(
            arxiv_id,
            extract_path
        )

        if tarball is None:
            obj.log.error("No tarball found")
            return
        add_file_by_name(model, tarball)
    else:
        tarball = existing_file.get_syspath()

    try:
        marcxml = get_marcxml_plots_from_tarball(tarball)
    except Timeout:
        eng.log.error(
            'Timeout during tarball extraction on {0}'.format(tarball)
        )

    if marcxml:
        # We store the path to the directory the tarball contents lives
        new_dict = get_json_from_marcxml(marcxml)[0]
        record.update(new_dict)
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
    from invenio.legacy.refextract.api import extract_references_from_file_xml

    model = eng.workflow_definition.model(obj)
    record = get_record_from_model(model)
    arxiv_id = get_arxiv_id_from_record(record)
    existing_file = get_file_by_name(model, "{0}.pdf".format(arxiv_id))
    import ipdb; ipdb.set_trace()
    if not existing_file:
        # We download it
        extract_path = os.path.join(
            cfg.get('OAIHARVESTER_STORAGEDIR', cfg.get('CFG_TMPSHAREDDIR')),
            str(eng.uuid)
        )

        pdf = get_pdf_from_arxiv(
            arxiv_id,
            extract_path
        )

        if pdf is None:
            obj.log.error("No pdf found")
            return
        add_file_by_name(model, pdf)
    else:
        pdf = existing_file.get_syspath()

    if pdf and os.path.isfile(pdf):
        references_xml = extract_references_from_file_xml(pdf)
        if references_xml:
            updated_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                          '<collection>\n' + references_xml + \
                          "\n</collection>"
            new_dict = get_json_from_marcxml(updated_xml)[0]
            if "references" in new_dict:
                record["references"] = new_dict["references"]
                obj.log.info("Extracted {0} references".format(
                    len(obj.data["references"])
                ))
                obj.update_task_results(
                    "References",
                    [{"name": "References",
                      "result": new_dict['references'],
                      "template": "workflows/results/refextract.html"}]
                )
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
        from invenio.legacy.bibrecord import create_records, record_xml_output
        from invenio.legacy.bibconvert.xslt_engine import convert
        from invenio.utils.plotextractor.api import get_tarball_from_arxiv
        from invenio.utils.plotextractor.cli import get_defaults
        from invenio.modules.workflows.utils import convert_marcxml_to_bibfield
        from invenio.utils.plotextractor.converter import untar
        from invenio.utils.shell import Timeout

        from ..utils import find_matching_files

        identifiers = obj.data.get(cfg.get('OAIHARVESTER_RECORD_ARXIV_ID_LOOKUP'), "")
        if "_result" not in obj.extra_data:
            obj.extra_data["_result"] = {}
        if "tarball" not in obj.extra_data["_result"]:
            extract_path = os.path.join(
                cfg.get('OAIHARVESTER_STORAGEDIR', cfg.get('CFG_TMPSHAREDDIR')),
                str(eng.uuid)
            )
            tarball = get_tarball_from_arxiv(
                obj.data.get(cfg.get('OAIHARVESTER_RECORD_ARXIV_ID_LOOKUP')),
                extract_path
            )
            if tarball is None:
                obj.log.error("No tarball found")
                return
        else:
            tarball = obj.extra_data["_result"]["tarball"]

        # FIXME
        tarball = str(tarball)
        sub_dir, dummy = get_defaults(tarball,
                                      cfg['CFG_TMPDIR'], "")

        try:
            untar(tarball, sub_dir)
            obj.log.info("Extracted tarball to: {0}".format(sub_dir))
        except Timeout:
            eng.log.error('Timeout during tarball extraction on %s' % (
                obj.extra_data["_result"]["tarball"]))

        xml_files_list = find_matching_files(sub_dir, ["xml"])

        obj.log.info("Found xmlfiles: {0}".format(xml_files_list))

        authors = ""

        for xml_file in xml_files_list:
            xml_file_fd = open(xml_file, "r")
            xml_content = xml_file_fd.read()
            xml_file_fd.close()

            match = REGEXP_AUTHLIST.findall(xml_content)
            if match:
                obj.log.info("Found a match for author extraction")
                authors = convert(xml_content, stylesheet)
                authorlist_record = create_records(authors)
                if len(authorlist_record) == 1:
                    if authorlist_record[0][0] is None:
                        eng.log.error("Error parsing authorlist record for id: %s" % (
                            identifiers,))
                    authorlist_record = authorlist_record[0][0]

                author_xml = record_xml_output(authorlist_record)
                if author_xml:
                    updated_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<collection>\n' \
                                  + record_xml_output(authorlist_record) + '</collection>'
                    new_dict_representation = convert_marcxml_to_bibfield(updated_xml)
                    obj.data["authors"] = new_dict_representation["authors"]
                    obj.update_task_results(
                        "authors",
                        [{
                            "name": "authors",
                            "results": new_dict_representation["authors"]
                        }]
                    )
                    obj.update_task_results(
                        "number_of_authors",
                        [{
                            "name": "number_of_authors",
                            "results": new_dict_representation["number_of_authors"]
                        }]
                    )
                    break
    return _author_list
