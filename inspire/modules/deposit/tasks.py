# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

"""Inspire deposit workflow tasks."""

import os
import requests
from tempfile import mkstemp

from invenio.base.globals import cfg
from invenio.modules.deposit.models import (
    Deposition,
    DepositionFile,
    FilenameAlreadyExists
)
from invenio.modules.deposit.storage import DepositionStorage


#
# Workflow tasks
#
def arxiv_fft_get(obj, eng):
    """Get FFT from arXiv, if arXiv ID is provided."""
    deposition = Deposition(obj)
    sip = deposition.get_latest_sip(sealed=False)
    metadata = sip.metadata

    if 'arxiv_id' in metadata and metadata['arxiv_id']:
        arxiv_pdf_url = cfg.get("ARXIV_PDF_URL", "http://arxiv.org/pdf/") + \
            "{0}.{1}"

        arxiv_pdf = requests.get(arxiv_pdf_url.format(
                                 metadata['arxiv_id'], "pdf"))

        from invenio.config import CFG_TMPSHAREDDIR
        arxiv_file, arxiv_file_path = mkstemp(
            prefix="%s_" % (metadata['arxiv_id'].replace("/", "_")),
            suffix='.pdf',
            dir=CFG_TMPSHAREDDIR,
        )

        os.write(arxiv_file, arxiv_pdf.content)
        os.close(arxiv_file)

        with open(arxiv_file_path) as fd:
            # To get 1111.2222.pdf as filename.
            filename = "{0}.pdf".format(metadata['arxiv_id'].replace("/", "_"))

            df = DepositionFile(backend=DepositionStorage(deposition.id))
            if df.save(fd, filename=filename):
                try:
                    deposition.add_file(df)
                    deposition.save()
                except FilenameAlreadyExists as e:
                    df.delete()
                    obj.log.error(str(e))


def add_submission_extra_data(obj, eng):
    """ Add extra data to workflow object. """
    deposition = Deposition(obj)
    sip = deposition.get_latest_sip(sealed=False)
    metadata = sip.metadata
    submission_data = {}
    if "references" in metadata:
        submission_data["references"] = metadata["references"]
        del metadata["references"]
    if "extra_comments" in metadata:
        submission_data["extra_comments"] = metadata["extra_comments"]
        del metadata["extra_comments"]
    if "url" in metadata:
        submission_data["url"] = metadata["url"]
        del metadata["url"]
    obj.extra_data["submission_data"] = submission_data
    deposition.save()


def extract_references(obj, eng):
    """If any, extract references from pdf or references box."""
    from invenio.legacy.refextract.api import (
        extract_references_from_url_xml,
        extract_references_from_string
    )

    references = None
    user_pdf = obj.extra_data.get("submission_data").get("pdf")
    user_references = obj.extra_data.get("submission_data").get("references")

    if user_pdf:
        pdf_file_request = requests.get(user_pdf)

        if pdf_file_request.headers.get('content-type') != 'application/pdf' or \
                pdf_file_request.status_code != 200:
            obj.log.error("No PDF file. Skipping!")
        else:
            try:
                references = extract_references_from_url_xml(user_pdf)
            except:
                obj.log.error("Not a file. Skipping!")
    elif user_references:
        references = extract_references_from_string(user_references)

    if references:
        from invenio.modules.workflows.utils import convert_marcxml_to_bibfield
        obj.log.info("Found references.")
        deposition = Deposition(obj)
        sip = deposition.get_latest_sip(sealed=False)
        if user_pdf:
            references_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                             '<collection>\n' + references + \
                             '\n</collection>'

            dict_representation = convert_marcxml_to_bibfield(references_xml)
        else:
            dict_representation = references
        if 'reference' in sip.metadata:
            sip.metadata['reference'].append(dict_representation["reference"])
        elif isinstance(dict_representation['reference'], list):
            sip.metadata['reference'] = dict_representation['reference']
        else:
            sip.metadata['reference'] = [dict_representation['reference']]
        obj.log.info("Added references to sip metadata.")
        obj.add_task_result("References",
                            dict_representation['reference'],
                            "workflows/results/refextract.html")
