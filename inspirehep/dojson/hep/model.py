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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""HEP model definition."""

import types
from dojson import Overdo
from dojson.utils import force_list


def add_book_info(record, blob):
    """Add link to the appropriate book record."""
    if 'collections' in record:
        collections = [c['primary'].lower() for c in record['collections']
                       if 'primary' in c]
        if 'bookchapter' in collections:
            pubinfos = force_list(blob.get("773__", []))
            for pubinfo in pubinfos:
                if pubinfo.get('0'):
                    record['book'] = {
                        'recid': int(pubinfo['0'])
                    }


def custom_do(self, blob):
    """Custom do function that allows extra post-processing."""
    record = self._do(blob)
    add_book_info(record, blob)
    return record

hep = Overdo()
hep._do = hep.do
hep.do = types.MethodType(custom_do, hep)
hep2marc = Overdo()
