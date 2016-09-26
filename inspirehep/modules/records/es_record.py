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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Record subclass to fetch records from ElasticSearch."""

from __future__ import absolute_import, division, print_function

from datetime import datetime

import arrow
from elasticsearch.exceptions import NotFoundError

from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.api import Record

from inspirehep.utils.record_getter import (
    RecordGetterError,
    get_es_record_by_uuid
)


class ESRecord(Record):

    """Record class that fetches records from ElasticSearch."""

    @classmethod
    def get_record(cls, object_uuid, with_deleted=False):
        """Get record instance from ElasticSearch."""
        try:
            return cls(get_es_record_by_uuid(object_uuid))
        except RecordGetterError as e:
            if isinstance(e.cause, NotFoundError):
                # Raise this error so the interface will render a 404 page
                # rather than a 500
                raise PIDDoesNotExistError('es_record', object_uuid)
            else:
                raise

    @property
    def updated(self):
        """Get last updated timestamp."""
        return arrow.get(self['_updated']).naive
