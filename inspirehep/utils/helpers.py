# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""Various helpers for the overlay."""

from __future__ import absolute_import, division, print_function

from contextlib import closing
from six.moves.urllib.parse import urlsplit

import requests

from inspirehep.modules.pidstore.utils import get_pid_type_from_endpoint


def download_file(url, output_file=None, chunk_size=1024):
    """Download a file to specified location."""
    r = requests.get(
        url=url,
        stream=True
    )
    if r.status_code == 200:
        with open(output_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size):
                f.write(chunk)
    return output_file


def download_file_to_record(record, name, url):
    """Download a file to specified record."""
    with closing(requests.get(url=url, stream=True)) as req:
        if req.status_code == 200:
            record.files[name] = req.raw
            return record.files[name]


def get_json_for_plots(plots):
    """Return proper FFT format from plotextracted plots."""
    output_records = []
    index = 0
    for plot in plots:
        output_records.append(dict(
            url=plot.get('url'),
            docfile_type='Plot',
            description="{0:05d} {1}".format(index, "".join(plot.get('captions', []))),
            filename=plot.get('name'),
        ))
        index += 1
    return dict(fft=output_records)


def force_force_list(data):
    """Wrap data in list.

    We need to define this awkardly named method because DoJSON's method
    force_list returns tuples or None instead of lists.
    """
    if data is None:
        return []
    elif not isinstance(data, (list, tuple, set)):
        return [data]
    elif isinstance(data, (tuple, set)):
        return list(data)
    return data


def get_recid_from_url(reference):
    """Retrieve recid from record URL.

    If no recid can be parsed, return False.
    """
    try:
        res = int(reference.split('/')[-1])
    except (ValueError, AttributeError):
        res = False
    return res


def get_pid_type_from_ref(reference):
    """Return the ``pid_type`` corresponding to a record URL.

    The reference name corresponds to the ``endpoint`` in all cases.
    This implementation exploits this by falling back to
    ``get_pid_type_from_endpoint``.
    """
    endpoint = urlsplit(reference).path.split('/')[-2]

    return get_pid_type_from_endpoint(endpoint)
