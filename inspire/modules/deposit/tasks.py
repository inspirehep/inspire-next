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
                fft_exists = False
                # Do we already have the file attached?
                if metadata.get('fft') and arxiv_pdf.status_code == 200:
                    from hashlib import md5
                    arxiv_md5 = md5(arxiv_pdf.content).hexdigest()

                    # Its not a list if only one item. Urk.
                    if not isinstance(metadata['fft'], list):
                        ffts = [metadata["fft"]]
                    else:
                        ffts = metadata["fft"]

                    fft_exists = filter(lambda fft: arxiv_md5 == md5(
                        open(fft['url']).read()).hexdigest(), ffts)

                    if not fft_exists:
                        deposition.add_file(df)
                else:
                    return
                if not fft_exists:
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
    obj.extra_data["submission_data"] = submission_data
    deposition.save()
