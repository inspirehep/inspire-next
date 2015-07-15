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
from tempfile import mkstemp

from invenio.base.globals import cfg
from invenio.modules.deposit.models import (
    Deposition,
    DepositionFile,
    FilenameAlreadyExists
)
from invenio.modules.deposit.storage import DepositionStorage
from invenio.utils.filedownload import download_url


#
# Helper functions
#
def save_deposition_file(deposition, filename, file_path):
    """Save files in Deposition."""
    with open(file_path) as fd:
        df = DepositionFile(backend=DepositionStorage(deposition.id))
        if df.save(fd, filename=filename):
            deposition.add_file(df)
            deposition.save()


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

        from invenio.config import CFG_TMPSHAREDDIR
        arxiv_file, arxiv_file_path = mkstemp(
            prefix="%s_" % (metadata['arxiv_id'].replace("/", "_")),
            suffix='.pdf',
            dir=CFG_TMPSHAREDDIR,
        )
        os.close(arxiv_file)

        download_url(url=arxiv_pdf_url.format(
                       metadata['arxiv_id'], "pdf"),
                     content_type="pdf",
                     download_to_file=arxiv_file_path)

        # To get 1111.2222.pdf as filename.
        filename = "{0}.pdf".format(metadata['arxiv_id'].replace("/", "_"))

        try:
            try:
                save_deposition_file(deposition,
                                     filename,
                                     arxiv_file_path)
            except FilenameAlreadyExists:
                obj.log.error("PDF file not saved: filename already exists.")
        except Exception as e:
            obj.log.error("PDF file not saved: {}.".format(e.message))


def add_submission_extra_data(obj, eng):
    """ Add extra data to workflow object. """
    deposition = Deposition(obj)
    sip = deposition.get_latest_sip(sealed=True)
    metadata = sip.metadata
    submission_data = {}
    if "references" in metadata:
        submission_data["references"] = metadata["references"]
        del metadata["references"]
    if "extra_comments" in metadata:
        submission_data["extra_comments"] = metadata["extra_comments"]
        del metadata["extra_comments"]
    if "pdf" in metadata:
        submission_data["pdf"] = metadata["pdf"]
        del metadata["pdf"]
    obj.extra_data["submission_data"] = submission_data
    deposition.save()
