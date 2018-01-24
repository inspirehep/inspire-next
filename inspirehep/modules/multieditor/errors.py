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

from __future__ import absolute_import, division, print_function


class InvalidActions(Exception):
    """Invalid action exception."""


class SchemaError(Exception):
    """Exception that handles faulty or missing schema"""
    def __init__(self):
        super(SchemaError, self).__init__("Invalid or missing schema")


class InvalidValue(Exception):
    """Exception that handles a non schema serializable value"""
    def __init__(self, value):
        super(InvalidValue, self).__init__("The value {0} cant be serialized for this field".format(value))
