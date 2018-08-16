# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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


class BaseOrcidPusherException(Exception):
    def __init__(self, from_exc=None, *args, **kwargs):
        # Sort of exception chaining in Python 2.
        # No need in Python 3 with the statement: raise exc from cause
        self.from_exc = from_exc
        super(BaseOrcidPusherException, self).__init__(*args, **kwargs)

    def __str__(self, *args, **kwargs):
        output = super(BaseOrcidPusherException, self).__str__(*args, **kwargs)
        if not self.from_exc:
            return output
        output += '\nThis exception was directly caused by the following exception:\n{}'.format(
            repr(self.from_exc))
        return output


class RecordNotFoundException(BaseOrcidPusherException):
    pass


class InputDataInvalidException(BaseOrcidPusherException):
    """
    The underneath Orcid service client response included an error related
    to input data like TokenInvalidException, OrcidNotFoundException,
    PutcodeNotFoundPutException.
    Note: that re-trying would not help in this case.
    """
    pass


class PutcodeNotFoundInOrcidException(BaseOrcidPusherException):
    """
    No putcode was found in ORCID API.
    """
    pass


class PutcodeNotFoundInCacheAfterCachingAllPutcodes(BaseOrcidPusherException):
    """
    No putcode was found in cache after having cached all author putcodes.
    """
    pass
