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

from __future__ import absolute_import, division, print_function

from functools import wraps

from flask import current_app
from werkzeug.utils import import_string

from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record

from inspirehep.modules.pidstore.providers import get_pid_type_for, get_endpoint_from_pid_type


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
def get_es_record(record_type, recid, **kwargs):
    pid = PersistentIdentifier.get(get_pid_type_for(record_type), recid)
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][record_type]
    search_class = import_string(search_conf['search_class'])()
    return search_class.get_source(pid.object_uuid, **kwargs)


def get_es_records(record_type, recids, **kwargs):
    """Get a list of recids from ElasticSearch.

    :param record_type: pid type of recids.
    :type record_type: string.
    :param recids: list of recids to retrieve.
    :type recids: list of strings.
    :returns: list of dictionaries with ES results
    """
    uuids = PersistentIdentifier.query.filter(
        PersistentIdentifier.pid_value.in_(recids),
        PersistentIdentifier.pid_type == get_pid_type_for(record_type)
    ).all()
    uuids = [str(uuid.object_uuid) for uuid in uuids]
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][record_type]
    search_class = import_string(search_conf['search_class'])()
    return search_class.mget(uuids, **kwargs)


@raise_record_getter_error_and_log
def get_es_record_by_uuid(uuid):
    pid = PersistentIdentifier.query.filter_by(object_uuid=uuid).one()
    search_conf = current_app.config['RECORDS_REST_ENDPOINTS'][get_endpoint_from_pid_type(pid.pid_type)]
    search_class = import_string(search_conf['search_class'])()
    return search_class.get_source(uuid)


@raise_record_getter_error_and_log
def get_db_record(record_type, recid):
    pid = PersistentIdentifier.get(get_pid_type_for(record_type), recid)
    return Record.get_record(pid.object_uuid)
