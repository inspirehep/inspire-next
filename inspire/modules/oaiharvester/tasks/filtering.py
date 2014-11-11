# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from functools import wraps


def get_content_from_files(name):
    """Task returning a list of all contents from a list of paths."""
    @wraps(get_content_from_files)
    def _get_content_from_files(obj, eng):
        list_of_filepaths = obj.extra_data[name]
        content_list = []
        for filepath in list_of_filepaths:
            with open(filepath) as fd:
                content_list.append(fd.read())
        obj.log.info("Read {0} files".format(len(list_of_filepaths)))
        return content_list

    return _get_content_from_files
