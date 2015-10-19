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

"""Helpers for arXiv.org."""

import os

from .helpers import download_file


def get_tarball(arxiv_id, output_directory):
    """Make a robotupload request."""
    arxiv_id = arxiv_id.replace("arXiv:", '')
    output_file = os.path.join(output_directory, "{0}.tar.gz".format(arxiv_id))
    url = "http://arxiv.org/e-print/{0}".format(arxiv_id)
    return download_file(url, output_file)


def get_pdf(arxiv_id, output_directory):
    """Make a robotupload request."""
    arxiv_id = arxiv_id.replace("arXiv:", '')
    output_file = os.path.join(output_directory, "{0}.pdf".format(arxiv_id))
    url = "http://arxiv.org/pdf/{0}".format(arxiv_id)
    return download_file(url, output_file)
