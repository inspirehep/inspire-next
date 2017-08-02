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

"""Resource-aware json reference loaders to be used with jsonref."""

from __future__ import absolute_import, division, print_function

from functools import wraps

from flask import current_app
from werkzeug.utils import import_string

from invenio_pidstore.models import PersistentIdentifier

from inspirehep.modules.pidstore.utils import get_endpoint_from_pid_type


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
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            current_app.logger.exception("Can't load recid %s", args)
            raise RecordGetterError(e.message, e)

    return wrapper


@raise_record_getter_error_and_log
def get_es_record(pid_type, recid, **kwargs):
    pid = PersistentIdentifier.get(pid_type, recid)

    endpoint = get_endpoint_from_pid_type(pid_type)
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][endpoint]
    search_class = import_string(search_conf['search_class'])()

    return search_class.get_source(pid.object_uuid, **kwargs)


def get_es_records(pid_type, recids, **kwargs):
    """Get a list of recids from ElasticSearch."""
    recids = [str(recid) for recid in recids]
    uuids = PersistentIdentifier.query.filter(
        PersistentIdentifier.pid_value.in_(recids),
        PersistentIdentifier.pid_type == pid_type
    ).all()
    uuids = [str(uuid.object_uuid) for uuid in uuids]

    endpoint = get_endpoint_from_pid_type(pid_type)
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][endpoint]
    search_class = import_string(search_conf['search_class'])()

    return search_class.mget(uuids, **kwargs)


@raise_record_getter_error_and_log
def get_es_record_by_uuid(uuid):
    pid = PersistentIdentifier.query.filter_by(object_uuid=uuid).one()

    endpoint = get_endpoint_from_pid_type(pid.pid_type)
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][endpoint]
    search_class = import_string(search_conf['search_class'])()

    return search_class.get_source(uuid)


@raise_record_getter_error_and_log
def get_db_record(pid_type, recid):
    from inspirehep.modules.records.api import InspireRecord
    pid = PersistentIdentifier.get(pid_type, recid)
    return InspireRecord.get_record(pid.object_uuid)
