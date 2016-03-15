# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Resource-aware json reference loaders to be used with jsonref."""

from functools import wraps

from flask import current_app

from invenio_records.api import Record
from invenio_pidstore.models import PersistentIdentifier
from invenio_search import current_search_client as es


class RecordGetterError(Exception):

    def __init__(self, message, cause):
        super(RecordGetterError, self).__init__(message)
        self.cause = cause

    def __repr__(self):
        return '{} caused by {}'.format(
            super(RecordGetterError, self).__repr__(),
            repr(self.cause)
        )

    def __str__(self):
        return repr(self)


def raise_record_getter_error_and_log(f):
    @wraps(f)
    def wrapper(record_type, recid):
        try:
            return f(record_type, recid)
        except Exception as e:
            current_app.logger.error('Error in retrieving record [{0}:{1}] '
                                     'caused by {2}'.format(record_type, recid,
                                                            repr(e)))
            raise RecordGetterError(e.message, e)

    return wrapper


@raise_record_getter_error_and_log
def get_es_record(record_type, recid):
    pid = PersistentIdentifier.get(record_type, recid)
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][record_type]

    return es.get_source(
        index=search_conf['search_index'],
        id=str(pid.object_uuid),
        doc_type=search_conf['search_type'])


@raise_record_getter_error_and_log
def get_db_record(record_type, recid):
    pid = PersistentIdentifier.get(record_type, recid)
    return Record.get_record(pid.object_uuid)
