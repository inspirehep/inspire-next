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

"""Tasks related to record merging."""

from __future__ import absolute_import, division, print_function

from invenio_pidstore.resolver import PersistentIdentifier

from inspirehep.utils.record import get_source, get_recid

from ..utils import with_debug_logging, retrieve_root_json as _retrieve_root_json

@with_debug_logging
def retrieve_root_json(obj, eng):
    """Retrieve the root JSON.

    Retrieves the root JSON corresponding to the current matched record and the
    provided source.
    The root version is stored in `obj.extra_data['root_json']`.
    """
    source = get_source(obj.metadata)
    recid = get_recid(obj.metadata)
    record_uuid = PersistentIdentifier.get('literature', recid).object_uuid
    obj.extra_data['root_json'] = _retrieve_root_json(record_uuid, source)
