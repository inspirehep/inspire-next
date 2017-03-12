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

"""Various helpers for the overlay."""

from __future__ import absolute_import, division, print_function

from contextlib import closing

import requests


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


def download_file_to_workflow(workflow, name, url):
    """Download a file to a specified workflow.

    The ``workflow.files`` property is actually a method, which returns a
    ``WorkflowFilesIterator``. This class inherits a custom ``__setitem__``
    method from its parent, ``FilesIterator``, which ends up calling ``save``
    on an ``invenio_files_rest.storage.pyfs.PyFSFileStorage`` instance
    through ``ObjectVersion`` and ``FileObject``. This method consumes the
    stream passed to it and saves in its place a ``FileObject`` with the
    details of the downloaded file.
    """
    with closing(requests.get(url=url, stream=True)) as req:
        if req.status_code == 200:
            workflow.files[name] = req.raw
            return workflow.files[name]


def get_json_for_plots(plots):
    """Return proper FFT format from plotextracted plots."""
    output_records = []
    index = 0
    for plot in plots:
        output_records.append(dict(
            path=plot.get('url'),
            type='Plot',
            description="{0:05d} {1}".format(index, "".join(plot.get('captions', []))),
            filename=plot.get('name'),
        ))
        index += 1
    return dict(_fft=output_records)


def force_list(data):
    """Force ``data`` to become a list.

    You should use this method whenever you don't want to deal with the
    fact that ``NoneType`` can't be iterated over. For example, instead
    of writing::

        bar = foo.get('bar')
        if bar is not None:
            for el in bar:
                ...

    you can write::

        for el in force_list(foo.get('bar')):
            ...

    Args:
        data: any Python object.

    Returns:
        list: a list representation of ``data``.

    Examples:
        >>> force_list(None)
        []
        >>> force_list('foo')
        ['foo']
        >>> force_list(('foo', 'bar'))
        ['foo', 'bar']
        >>> force_list(['foo', 'bar', 'baz'])
        ['foo', 'bar', 'baz']

    """
    if data is None:
        return []
    elif not isinstance(data, (list, tuple, set)):
        return [data]
    elif isinstance(data, (tuple, set)):
        return list(data)
    return data
