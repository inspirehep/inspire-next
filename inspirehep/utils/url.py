# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Helpers for handling with http requests and URL handling."""

from __future__ import absolute_import, division, print_function

import io
import tempfile

import requests
from contextlib import contextmanager
from flask import current_app
from fs.opener import fsopen

from inspire_utils.urls import record_url_by_pattern
from inspirehep import __version__


def make_user_agent_string(component=""):
    """Return a nice and uniform user-agent string to be used by INSPIRE."""
    ret = "InspireHEP-{0} (+{1};)".format(
        __version__,
        current_app.config.get('SERVER_NAME', ''),
    )
    if component:
        ret += " [{}]".format(component)
    return ret


def is_pdf_link(url):
    """Return ``True`` if ``url`` points to a PDF.

    Returns ``True`` if the first significant line of the response starts with
    ``%PDF``.

    Args:
        url (string): a URL.

    Returns:
        bool: whether the url points to a PDF.

    """
    try:
        response = requests.get(url, allow_redirects=True, stream=True)
    except requests.exceptions.RequestException:
        return False

    try:
        first_significant_line = next(response.iter_lines(1))
        while not first_significant_line.strip():
            first_significant_line = next(response.iter_lines(1))
    except StopIteration:
        return False

    return first_significant_line.startswith('%PDF')


def copy_file(src_file, dst_file, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """Dummy buffered copy between open files."""
    next_chunk = src_file.read(buffer_size)
    while next_chunk:
        dst_file.write(next_chunk)
        next_chunk = src_file.read(buffer_size)


@contextmanager
def retrieve_uri(uri, outdir=None):
    """Retrieves the given uri and stores it in a temporary file."""
    with tempfile.NamedTemporaryFile(prefix='inspire', dir=outdir) as local_file, \
            fsopen(uri, mode='rb') as remote_file:
        copy_file(remote_file, local_file)

        local_file.flush()
        yield local_file.name


def get_legacy_url_for_recid(recid):
    """Get a URL to a record on INSPIRE.

    Args:
        recid (Union[int, string]): record ID
        pattern_config_var (string): config var with the pattern

    Return:
        text_type: URL
    """
    pattern = current_app.config['LEGACY_RECORD_URL_PATTERN']
    return record_url_by_pattern(pattern, recid)
