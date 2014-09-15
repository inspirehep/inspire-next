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
from werkzeug.utils import secure_filename

from invenio.base.globals import cfg
from invenio.modules.deposit.models import Deposition, DepositionFile
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
            prefix="%s_" % (metadata['arxiv_id']),
            suffix='.pdf',
            dir=CFG_TMPSHAREDDIR,
        )

        os.write(arxiv_file, arxiv_pdf.content)
        os.close(arxiv_file)

        f = open(arxiv_file_path)
        filename = secure_filename(arxiv_file_path)
        df = DepositionFile(backend=DepositionStorage(deposition.id))

        if df.save(f, filename=filename):
            if 'fft' in metadata and metadata['fft'] and \
                    arxiv_pdf.status_code == 200:
                from hashlib import md5
                arxiv_md5 = md5(arxiv_pdf.content).hexdigest()

                fft_exists = filter(lambda fft: arxiv_md5 == md5(
                    open(fft['url']).read()).hexdigest(), metadata['fft'])

                if not fft_exists:
                    deposition.add_file(df)
            else:
                deposition.add_file(df)

    deposition.save()
